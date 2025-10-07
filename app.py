#!/usr/bin/env python3
"""
Linkbuilding Artikel Generator Backend
Generates articles using OpenAI GPT-4o with AUTO TOPIC generation and CHAT refinement
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from openai import OpenAI
import httpx
import requests
import json
import os
import re

app = Flask(__name__)
CORS(app)

# Load API keys from environment variables (for Render.com)
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
ORIGINALITY_API_KEY = os.environ.get('ORIGINALITY_API_KEY')

# Initialize OpenAI client with custom httpx client to avoid proxy issues
client = None
if OPENAI_API_KEY:
    # Create custom httpx client without proxy configuration
    http_client = httpx.Client(
        timeout=60.0,
        follow_redirects=True
    )
    client = OpenAI(
        api_key=OPENAI_API_KEY,
        http_client=http_client
    )
    print("✅ OpenAI API key loaded with custom HTTP client")
else:
    print("⚠️  OpenAI API key not found in environment")

if ORIGINALITY_API_KEY:
    print("✅ Originality.AI API key loaded")
else:
    print("⚠️  Originality.AI API key not found in environment")

# Topic generation prompt - UPDATED: NO keywords, NO product names
TOPIC_GENERATION_PROMPT = """Je bent een SEO expert die perfecte artikel onderwerpen bedenkt voor linkbuilding.

Gegeven deze twee anchor teksten:
1. "{anchor1}"
2. "{anchor2}"

Bedenk een relevant, natuurlijk artikel onderwerp dat beide anchor teksten logisch kan bevatten.

KRITIEKE EISEN VOOR HET ONDERWERP:
✅ Het onderwerp moet ALGEMEEN en BREED zijn
✅ GEEN specifieke productnamen of modellen (zoals "Golf 8", "Audi A3", etc.)
✅ GEEN keywords of merknamen in het onderwerp
✅ Vraagvorm of informatief
✅ Maximaal 10 woorden
✅ Nederlands
✅ GEEN dubbele punten (:) of andere scheidingstekens
✅ GEEN jaartallen (zoals 2024, 2025, etc.)
✅ Geschikt als H1 titel voor een artikel

VOORBEELDEN VAN GOEDE ONDERWERPEN:
✅ "Waarom kiezen voor zakelijke lease"
✅ "Hoe kies je de juiste lease auto"
✅ "Wat zijn de kosten van zakelijk rijden"
✅ "Elektrisch of benzine voor zakelijk gebruik"

VOORBEELDEN VAN FOUTE ONDERWERPEN:
❌ "Golf 8 lease zakelijk" (bevat productnaam)
❌ "Audi A3 of BMW 3 Serie" (bevat merknamen)
❌ "Zakelijke lease: voordelen 2024" (bevat jaartal en dubbele punt)
❌ "Volkswagen Golf lease" (bevat merk en model)

{extra_context}

Geef ALLEEN het onderwerp terug, niets anders. Het onderwerp moet ALGEMEEN zijn zonder specifieke producten of merken."""

# Article generation prompt - UPDATED: H1 must be GENERAL, NO keywords
ARTICLE_PROMPT = """Je bent een professionele Nederlandse contentschrijver gespecialiseerd in SEO-artikelen voor de zakelijke leasemarkt. Je schrijft natuurlijke, menselijke teksten die NIET detecteerbaar zijn als AI-gegenereerd.

OPDRACHT:
Schrijf een artikel van PRECIES 500 woorden over: {onderwerp}

VERPLICHTE STRUCTUUR:
- 1x H1 (hoofdtitel) - gebruik EXACT het onderwerp: "{onderwerp}" - markeer met "H1: " ervoor
- 3x H2 (hoofdsecties) - markeer met "H2: " ervoor
- 2x H3 (subsecties) - markeer met "H3: " ervoor
- Intro alinea (zonder heading)
- Conclusie sectie (met H2: Conclusie)

ANCHOR TEKSTEN (SUBTIEL VERWERKEN):
Verwerk deze twee anchor teksten SUBTIEL en NATUURLIJK in de lopende tekst:
1. "{anchor1}" → link naar: {url1}
2. "{anchor2}" → link naar: {url2}

KRITIEKE REGELS VOOR ANCHOR TEKSTEN:
✅ Gebruik elke anchor tekst PRECIES 1 KEER in het hele artikel
✅ Noem ze SUBTIEL in de lopende tekst, niet prominent
✅ GEEN actieve promotie of verkoop-taal
✅ Gewoon terloops noemen als voorbeeld of optie
✅ Bijvoorbeeld: "...zoals de {anchor1}, die..." of "...denk aan de {anchor2}..."
❌ NIET: "Bekijk de {anchor1}!" of "Kies voor de {anchor2}!"
❌ NIET meerdere keren dezelfde anchor tekst gebruiken

HEADINGS - ZEER BELANGRIJK:
✅ H1: Gebruik EXACT het onderwerp "{onderwerp}" (met "H1: " ervoor)
✅ H1 moet ALGEMEEN zijn - GEEN productnamen, merknamen, of keywords
✅ Markeer alle headings met "H1: ", "H2: ", "H3: " ervoor (dit wordt later omgezet naar echte HTML headings)
✅ Gebruik natuurlijke, informatieve headings
✅ Headings moeten algemeen en leesbaar zijn
✅ GEEN keywords of productnamen in headings
✅ Laatste H2 moet zijn: "H2: Conclusie" (met hoofdletter C)
✅ Bijvoorbeeld:
   - "H1: Waarom kiezen voor zakelijke lease" (GOED - algemeen)
   - "H1: Golf 8 lease zakelijk" (FOUT - bevat productnaam)
   - "H2: Praktische overwegingen" (GOED)
   - "H2: Golf 8 lease zakelijk voordelen" (FOUT - dit is een keyword)
   - "H2: Conclusie" (GOED - met hoofdletter)
   - "H2: conclusie" (FOUT - kleine letter)

VERBODEN WOORDEN:
❌ NOOIT het woord "voordelen" gebruiken
❌ Gebruik alternatieven: pluspunten, sterke punten, wat het biedt, waarom het werkt, etc.

SCHRIJFSTIJL - ZEER BELANGRIJK:

WEL doen:
✅ Gebruik ALTIJD "je" en "jij" (NOOIT "u")
✅ Korte, pakkende zinnen
✅ Afwisselende zinslengte (kort-lang-kort ritme)
✅ Directe aanspreking ("je", "jouw", "jij")
✅ Retorische vragen
✅ Natuurlijke taalfouten en variaties:
   - Soms een zin beginnen met "En", "Maar", "Want", "Plus"
   - Af en toe een incomplete zin voor effect
   - Variatie in interpunctie (. ! ?)
✅ Concrete voorbeelden en details
✅ Professioneel maar toegankelijk
✅ Menselijke observaties ("Klinkt gek misschien", "Dat tikt aan")

NIET doen:
❌ NOOIT "u" gebruiken - ALTIJD "je" en "jij"
❌ NOOIT "voordelen" zeggen
❌ GEEN keywords in headings
❌ GEEN productnamen of merknamen in H1
❌ GEEN actieve promotie van producten/links
❌ GEEN anchor tekst meer dan 1 keer gebruiken
❌ GEEN "conclusie" met kleine letter - ALTIJD "Conclusie" met hoofdletter
❌ Geen Engelse woorden (check → controleer/bekijk)
❌ Geen afkortingen ('m, 'n, 't)
❌ Geen AI-clichés zoals:
   - "In de wereld van..."
   - "Het is belangrijk om te..."
   - "Laten we eens kijken naar..."
   - "Aan de andere kant..."
   - "Bovendien..."
   - "Daarnaast is het essentieel..."
❌ Geen perfecte, gepolijste zinnen
❌ Geen opsommingen met bullets
❌ Geen overdreven enthousiasme
❌ Geen marketing-taal of buzzwords

TOON:
- Professioneel maar niet stijf
- Praktisch en direct
- Alsof een ervaren ondernemer advies geeft aan een collega
- Geen verkoop-pitch, maar eerlijk advies
- Licht conversationeel zonder te casual te zijn
- Gebruik "je" en "jij" consequent
- Producten/links subtiel noemen, niet pushen

TECHNISCHE EISEN:
- Woordenaantal: EXACT 500 woorden (±2 woorden toegestaan)
- Anchor teksten: Beide verplicht, PRECIES 1 KEER elk, SUBTIEL verweven
- H1: EXACT het onderwerp "{onderwerp}" - moet ALGEMEEN zijn zonder keywords
- Headings: Natuurlijk en algemeen, GEEN keywords, WEL met "H1: ", "H2: ", "H3: " prefix
- Conclusie: ALTIJD "H2: Conclusie" met hoofdletter C
- Alinea's: 2-4 zinnen per alinea
- Geen intro zoals "In dit artikel..." - begin direct met de kern

{extra_context}

Schrijf nu het artikel. Begin direct met de H1 titel: "H1: {onderwerp}". H1 moet ALGEMEEN zijn. Gebruik ALTIJD "je" en "jij". Headings ZONDER keywords. Elke anchor PRECIES 1 KEER. NOOIT "voordelen". Conclusie met hoofdletter."""

def generate_topic(anchor1, anchor2, extra=""):
    """Generate article topic based on anchor texts using GPT-4o"""
    
    if not client:
        raise Exception("OpenAI API key not configured")
    
    extra_context = ""
    if extra:
        extra_context = f"\nEXTRA CONTEXT:\n{extra}"
    
    prompt = TOPIC_GENERATION_PROMPT.format(
        anchor1=anchor1,
        anchor2=anchor2,
        extra_context=extra_context
    )
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Je bent een SEO expert die ALGEMENE artikel onderwerpen bedenkt. GEEN productnamen, merknamen, keywords, dubbele punten of jaartallen in het onderwerp."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=100
        )
        
        topic = response.choices[0].message.content.strip()
        topic = topic.strip('"').strip("'")
        
        # Remove colons and year numbers
        topic = topic.replace(':', '').replace('|', '').replace('-', ' ')
        topic = re.sub(r'\b20\d{2}\b', '', topic)  # Remove years like 2024, 2025
        topic = re.sub(r'\s+', ' ', topic).strip()  # Clean up extra spaces
        
        return topic
    except Exception as e:
        print(f"OpenAI Topic Generation Error: {e}")
        raise

def generate_article(onderwerp, anchor1, url1, anchor2, url2, extra=""):
    """Generate article using OpenAI GPT-4o"""
    
    if not client:
        raise Exception("OpenAI API key not configured")
    
    extra_context = ""
    if extra:
        extra_context = f"\nEXTRA CONTEXT:\n{extra}"
    
    prompt = ARTICLE_PROMPT.format(
        onderwerp=onderwerp,
        anchor1=anchor1,
        url1=url1,
        anchor2=anchor2,
        url2=url2,
        extra_context=extra_context
    )
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": f"Je bent een expert Nederlandse contentschrijver die menselijke, natuurlijke teksten schrijft met 'je' en 'jij'. H1 is EXACT '{onderwerp}' en moet ALGEMEEN zijn zonder keywords of productnamen. Headings ZONDER keywords. Elke anchor PRECIES 1 KEER. NOOIT 'voordelen'. Conclusie met hoofdletter."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.9,
            max_tokens=2000
        )
        
        article = response.choices[0].message.content.strip()
        
        # Fix any lowercase "conclusie" to "Conclusie"
        article = re.sub(r'^H2:\s*conclusie\s*$', 'H2: Conclusie', article, flags=re.MULTILINE | re.IGNORECASE)
        
        # Convert to HTML with proper headings and anchor links
        article = format_article_html(article, anchor1, url1, anchor2, url2)
        
        return article
    except Exception as e:
        print(f"OpenAI Error: {e}")
        raise

def format_article_html(article, anchor1, url1, anchor2, url2):
    """Convert article with H1/H2/H3 markers to HTML with proper headings and anchor links"""
    
    # Replace heading markers with HTML tags
    article = re.sub(r'^H1:\s*(.+)$', r'<h1>\1</h1>', article, flags=re.MULTILINE)
    article = re.sub(r'^H2:\s*(.+)$', r'<h2>\1</h2>', article, flags=re.MULTILINE)
    article = re.sub(r'^H3:\s*(.+)$', r'<h3>\1</h3>', article, flags=re.MULTILINE)
    
    # Replace anchor texts with clickable links (only first occurrence of each)
    # Escape special regex characters in anchor texts
    anchor1_escaped = re.escape(anchor1)
    anchor2_escaped = re.escape(anchor2)
    
    # Replace first occurrence of anchor1
    article = re.sub(
        f'({anchor1_escaped})',
        f'<a href="{url1}" target="_blank">\\1</a>',
        article,
        count=1
    )
    
    # Replace first occurrence of anchor2
    article = re.sub(
        f'({anchor2_escaped})',
        f'<a href="{url2}" target="_blank">\\1</a>',
        article,
        count=1
    )
    
    # Wrap paragraphs in <p> tags (text that's not already in tags)
    lines = article.split('\n')
    formatted_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # If line doesn't start with HTML tag, wrap in <p>
        if not line.startswith('<'):
            line = f'<p>{line}</p>'
        formatted_lines.append(line)
    
    return '\n'.join(formatted_lines)

def refine_article(article, topic, anchors, user_request, history=[]):
    """Refine article based on user request"""
    
    if not client:
        raise Exception("OpenAI API key not configured")
    
    # Strip HTML for refinement
    article_plain = re.sub(r'<[^>]+>', '', article)
    article_plain = re.sub(r'</[^>]+>', '', article_plain)
    
    # Convert back to H1/H2/H3 format for AI
    article_plain = article_plain.replace('<h1>', 'H1: ').replace('</h1>', '')
    article_plain = article_plain.replace('<h2>', 'H2: ').replace('</h2>', '')
    article_plain = article_plain.replace('<h3>', 'H3: ').replace('</h3>', '')
    
    system_prompt = f"""Je bent een expert Nederlandse contentschrijver die artikelen aanpast op basis van feedback.

HUIDIGE ARTIKEL ONDERWERP: {topic}

ANCHOR TEKSTEN DIE SUBTIEL BEHOUDEN MOETEN BLIJVEN (PRECIES 1 KEER ELK):
1. "{anchors['anchor1']}" → {anchors['url1']}
2. "{anchors['anchor2']}" → {anchors['url2']}

BELANGRIJKE REGELS:
- H1 moet EXACT zijn: "{topic}" en moet ALGEMEEN zijn zonder keywords of productnamen
- Gebruik ALTIJD "je" en "jij" (NOOIT "u")
- Behoud de anchor teksten SUBTIEL in de tekst (niet actief promoten)
- Gebruik elke anchor tekst PRECIES 1 KEER
- Blijf rond 500 woorden
- Headings ZONDER keywords of productnamen
- Headings met "H1: ", "H2: ", "H3: " prefix
- Conclusie ALTIJD met hoofdletter: "H2: Conclusie"
- NOOIT het woord "voordelen" gebruiken
- Schrijf natuurlijk en menselijk
- Geen AI-clichés
- Professioneel maar toegankelijk
- Producten/links subtiel noemen, niet pushen

Pas het artikel aan volgens de vraag van de gebruiker."""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"HUIDIG ARTIKEL:\n\n{article_plain}\n\nAANPASSING GEVRAAGD:\n{user_request}\n\nGeef het volledige aangepaste artikel terug met H1:, H2:, H3: markers. H1 moet EXACT '{topic}' zijn en ALGEMEEN zonder keywords. Conclusie met hoofdletter."}
    ]
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.8,
            max_tokens=2000
        )
        
        refined_article = response.choices[0].message.content.strip()
        
        # Fix any lowercase "conclusie" to "Conclusie"
        refined_article = re.sub(r'^H2:\s*conclusie\s*$', 'H2: Conclusie', refined_article, flags=re.MULTILINE | re.IGNORECASE)
        
        # Convert to HTML
        refined_article = format_article_html(
            refined_article,
            anchors['anchor1'],
            anchors['url1'],
            anchors['anchor2'],
            anchors['url2']
        )
        
        return refined_article
    except Exception as e:
        print(f"OpenAI Refinement Error: {e}")
        raise

def check_originality(text):
    """Check originality using Originality.AI multilingual model"""
    
    # Strip HTML tags for originality check
    text_plain = re.sub(r'<[^>]+>', '', text)
    
    if not ORIGINALITY_API_KEY:
        print("⚠️  Originality.AI key not configured, skipping check")
        return {
            'ai_score': 0,
            'human_score': 100,
            'success': True,
            'skipped': True
        }
    
    url = "https://api.originality.ai/api/v1/scan/ai"
    
    headers = {
        "X-OAI-API-KEY": ORIGINALITY_API_KEY,
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    payload = {
        "content": text_plain,
        "title": "Article Check",
        "aiModelVersion": "multi",
        "storeScan": "true"
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        
        ai_score = round(data['score']['ai'] * 100, 1)
        human_score = round(data['score']['original'] * 100, 1)
        
        # Get scan URL - use public_link if available, otherwise construct from id
        scan_url = None
        if 'public_link' in data:
            scan_url = data['public_link']
        elif 'id' in data:
            scan_url = f"https://app.originality.ai/scan/{data['id']}"
        
        print(f"✅ Originality check: AI={ai_score}%, Human={human_score}%, URL={scan_url}")
        
        return {
            'ai_score': ai_score,
            'human_score': human_score,
            'success': True,
            'scan_url': scan_url
        }
    except Exception as e:
        print(f"Originality.AI Error: {e}")
        return {
            'ai_score': 0,
            'human_score': 0,
            'success': False,
            'error': str(e)
        }

def count_words(text):
    """Count words in text"""
    # Strip HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    words = text.split()
    return len(words)

@app.route('/')
def index():
    """Serve the HTML frontend"""
    return send_file('article_generator_app.html')

@app.route('/generate_linkbuilding', methods=['POST'])
@app.route('/generate-article', methods=['POST'])
def generate_article_endpoint():
    """Generate article with auto topic and check originality"""
    
    try:
        data = request.json
        
        # Support both old and new format
        if 'anchor_texts' in data:
            # New format from frontend
            anchor_texts = data.get('anchor_texts', [])
            urls = data.get('urls', [])
            extra = data.get('context', '')
            
            if len(anchor_texts) < 2 or len(urls) < 2:
                return jsonify({
                    'success': False,
                    'error': 'Minimaal 2 anchor teksten en URLs vereist'
                }), 400
            
            anchor1 = anchor_texts[0]
            anchor2 = anchor_texts[1]
            url1 = urls[0]
            url2 = urls[1]
        else:
            # Old format
            anchor1 = data.get('anchor1')
            url1 = data.get('url1')
            anchor2 = data.get('anchor2')
            url2 = data.get('url2')
            extra = data.get('extra', '')
        
        if not all([anchor1, url1, anchor2, url2]):
            return jsonify({
                'success': False,
                'error': 'Alle verplichte velden moeten ingevuld zijn'
            }), 400
        
        # Always auto-generate topic for linkbuilding
        print(f"Generating topic for anchors: {anchor1}, {anchor2}")
        onderwerp = generate_topic(anchor1, anchor2, extra)
        print(f"Generated topic: {onderwerp}")
        
        print(f"Generating article for: {onderwerp}")
        article = generate_article(onderwerp, anchor1, url1, anchor2, url2, extra)
        
        # Strip HTML for plain text version
        article_text = re.sub(r'<[^>]+>', '', article)
        article_text = article_text.replace('</h1>', '\n').replace('</h2>', '\n').replace('</h3>', '\n').replace('</p>', '\n\n')
        article_text = re.sub(r'\n\n+', '\n\n', article_text).strip()
        
        word_count = count_words(article)
        print(f"Article generated: {word_count} words")
        
        print("Checking originality...")
        originality = check_originality(article)
        
        return jsonify({
            'success': True,
            'article_html': article,
            'article_text': article_text,
            'topic': onderwerp,
            'originality_data': {
                'human_score': originality['human_score'],
                'ai_score': originality['ai_score'],
                'report_url': originality.get('scan_url')
            },
            'word_count': word_count,
            # Legacy fields for backward compatibility
            'article': article,
            'wordCount': word_count,
            'humanScore': originality['human_score'],
            'aiScore': originality['ai_score'],
            'scanUrl': originality.get('scan_url'),
            'generatedTopic': onderwerp,
            'links': [
                {'text': anchor1, 'url': url1},
                {'text': anchor2, 'url': url2}
            ]
        })
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/refine_article', methods=['POST'])
@app.route('/refine-article', methods=['POST'])
def refine_article_endpoint():
    """Refine article based on user request"""
    
    try:
        data = request.json
        
        article = data.get('article')
        instruction = data.get('instruction')
        
        if not all([article, instruction]):
            return jsonify({
                'success': False,
                'error': 'Ontbrekende gegevens'
            }), 400
        
        # Extract topic and anchors from the article if not provided
        topic = data.get('topic', 'Artikel')
        anchors = data.get('anchors', {
            'anchor1': '',
            'url1': '',
            'anchor2': '',
            'url2': ''
        })
        
        print(f"Refining article: {instruction}")
        refined_article = refine_article(article, topic, anchors, instruction, [])
        
        # Strip HTML for plain text version
        article_text = re.sub(r'<[^>]+>', '', refined_article)
        article_text = article_text.replace('</h1>', '\n').replace('</h2>', '\n').replace('</h3>', '\n').replace('</p>', '\n\n')
        article_text = re.sub(r'\n\n+', '\n\n', article_text).strip()
        
        word_count = count_words(refined_article)
        print(f"Article refined: {word_count} words")
        
        print("Checking originality...")
        originality = check_originality(refined_article)
        
        return jsonify({
            'success': True,
            'article_html': refined_article,
            'article_text': article_text,
            'originality_data': {
                'human_score': originality['human_score'],
                'ai_score': originality['ai_score'],
                'report_url': originality.get('scan_url')
            },
            'word_count': word_count,
            # Legacy fields
            'article': refined_article,
            'wordCount': word_count,
            'humanScore': originality['human_score'],
            'aiScore': originality['ai_score'],
            'scanUrl': originality.get('scan_url'),
            'message': 'Artikel aangepast volgens jouw verzoek!'
        })
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("🚀 Starting Linkbuilding Artikel Generator...")
    print("🤖 MODEL: GPT-4o (GPT-4 Omni)")
    print("💬 CHAT: Aanpassingen vragen na generatie")
    print("✍️  STIJL: Schrijft met 'je' en 'jij'")
    print("🎯 H1: ALGEMEEN onderwerp, GEEN keywords/producten")
    print("📋 HEADINGS: Natuurlijk, GEEN keywords")
    print("🔗 LINKS: Klikbaar met anchor, PRECIES 1x elk")
    print("🚫 VERBODEN: 'voordelen'")
    print("✅ CONCLUSIE: Altijd met hoofdletter")
    print("📊 ORIGINALITY: Public scan link included")
    print(f"📍 Running on port: {port}")
    print("")
    if not client:
        print("⚠️  WARNING: OpenAI API key not configured!")
    app.run(host='0.0.0.0', port=port, debug=False)
