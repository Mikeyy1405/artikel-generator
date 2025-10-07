#!/usr/bin/env python3
"""
Writgo Academy Content Generator v11
Multi-feature content creation platform with WordPress integration
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from openai import OpenAI
import httpx
import requests
import json
import os
import re
from datetime import datetime
import sqlite3

app = Flask(__name__)
CORS(app)

# Database setup
DB_PATH = 'writgo_content.db'

def init_db():
    """Initialize SQLite database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Articles table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content_html TEXT NOT NULL,
            content_text TEXT NOT NULL,
            article_type TEXT DEFAULT 'linkbuilding',
            anchor1 TEXT,
            url1 TEXT,
            anchor2 TEXT,
            url2 TEXT,
            word_count INTEGER,
            human_score REAL,
            ai_score REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # WordPress sites table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS wordpress_sites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            site_name TEXT NOT NULL UNIQUE,
            site_url TEXT NOT NULL,
            username TEXT NOT NULL,
            app_password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Internal links per site
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS internal_links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            site_id INTEGER NOT NULL,
            anchor_text TEXT NOT NULL,
            url TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (site_id) REFERENCES wordpress_sites(id) ON DELETE CASCADE
        )
    ''')
    
    # Affiliate links per site
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS affiliate_links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            site_id INTEGER NOT NULL,
            anchor_text TEXT NOT NULL,
            url TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (site_id) REFERENCES wordpress_sites(id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized")

# Initialize database on startup
init_db()

# Load API keys
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
ORIGINALITY_API_KEY = os.environ.get('ORIGINALITY_API_KEY')
PIXABAY_API_KEY = os.environ.get('PIXABAY_API_KEY')

# Initialize OpenAI client
client = None
if OPENAI_API_KEY:
    http_client = httpx.Client(timeout=60.0, follow_redirects=True)
    client = OpenAI(api_key=OPENAI_API_KEY, http_client=http_client)
    print("✅ OpenAI API key loaded")
else:
    print("⚠️  OpenAI API key not found")

if ORIGINALITY_API_KEY:
    print("✅ Originality.AI API key loaded")
else:
    print("⚠️  Originality.AI API key not found")

# FORBIDDEN PHRASES - Comprehensive list with variations
FORBIDDEN_PHRASES = [
    "voordelen van",
    "voordelen",
    "voordeel van",
    "voordeel",
    "dat is best een opluchting, toch?",
    "dat is best een opluchting toch",
    "dat is best een opluchting"
]

def check_forbidden_words(text):
    """
    Check if text contains forbidden phrases (case-insensitive)
    Returns: (has_forbidden, list_of_found_phrases)
    """
    text_lower = text.lower()
    found_phrases = []
    
    for phrase in FORBIDDEN_PHRASES:
        # Use word boundaries to avoid false positives
        pattern = r'\b' + re.escape(phrase.lower()) + r'\b'
        if re.search(pattern, text_lower):
            found_phrases.append(phrase)
    
    return (len(found_phrases) > 0, found_phrases)

# Topic generation prompt
TOPIC_GENERATION_PROMPT = """Je bent een SEO expert die perfecte artikel onderwerpen bedenkt voor linkbuilding.

Gegeven deze twee anchor teksten:
1. "{anchor1}"
2. "{anchor2}"

Bedenk een relevant, natuurlijk artikel onderwerp dat beide anchor teksten logisch kan bevatten.

KRITIEKE EISEN VOOR HET ONDERWERP:
✅ Het onderwerp moet ALGEMEEN en BREED zijn
✅ GEEN specifieke productnamen of modellen
✅ GEEN keywords of merknamen in het onderwerp
✅ Vraagvorm of informatief
✅ Maximaal 10 woorden
✅ Nederlands
✅ GEEN dubbele punten (:) of andere scheidingstekens
✅ GEEN jaartallen
✅ Geschikt als H1 titel voor een artikel

{extra_context}

Geef ALLEEN het onderwerp terug, niets anders."""

# Article generation prompt - UPDATED with stronger forbidden words enforcement
ARTICLE_PROMPT = """Je bent een professionele Nederlandse contentschrijver. Je schrijft natuurlijke, menselijke teksten die NIET detecteerbaar zijn als AI-gegenereerd.

OPDRACHT:
Schrijf een artikel van PRECIES 500 woorden over: {onderwerp}

BELANGRIJK - DYNAMISCHE CONTENT:
✅ Schrijf SPECIFIEK over het onderwerp dat gegeven is
✅ GEEN vast thema of vaste invalshoek - pas je aan bij het onderwerp
✅ Analyseer het onderwerp en schrijf daar passend over
✅ Als het onderwerp een vraag is, beantwoord die vraag
✅ Als het onderwerp een statement is, werk dat uit
✅ Blijf relevant en on-topic voor het specifieke onderwerp

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

HEADINGS - ZEER BELANGRIJK:
✅ H1: Gebruik EXACT het onderwerp "{onderwerp}" (met "H1: " ervoor)
✅ H2 en H3: Maak deze RELEVANT voor het specifieke onderwerp
✅ H2 en H3: GEEN vaste templates of standaard koppen
✅ H2 en H3: Pas aan bij de inhoud en het onderwerp
✅ Markeer alle headings met "H1: ", "H2: ", "H3: " ervoor
✅ Laatste H2 moet zijn: "H2: Conclusie" (met hoofdletter C)

⚠️ VERBODEN WOORDEN EN ZINNEN - ZEER STRENG:
❌ ABSOLUUT VERBODEN: "voordelen" in ELKE vorm
❌ ABSOLUUT VERBODEN: "voordeel" in ELKE vorm
❌ ABSOLUUT VERBODEN: "voordelen van"
❌ ABSOLUUT VERBODEN: "voordeel van"
❌ ABSOLUUT VERBODEN: "Dat is best een opluchting, toch?"
❌ ABSOLUUT VERBODEN: "Dat is best een opluchting"

✅ GEBRUIK IN PLAATS DAARVAN:
- pluspunten
- sterke punten
- wat het biedt
- waarom het werkt
- de kracht van
- wat je ermee bereikt
- wat het je oplevert
- de meerwaarde
- het nut van
- de waarde van
- wat het bijzonder maakt
- waarom het interessant is

SCHRIJFSTIJL - ZEER BELANGRIJK:

WEL doen:
✅ Gebruik ALTIJD "je" en "jij" (NOOIT "u")
✅ Korte, pakkende zinnen
✅ Afwisselende zinslengte
✅ Directe aanspreking
✅ Retorische vragen
✅ Natuurlijke taalfouten en variaties
✅ Concrete voorbeelden
✅ Professioneel maar toegankelijk
✅ Schrijf SPECIFIEK over het gegeven onderwerp

NIET doen:
❌ NOOIT "u" gebruiken - ALTIJD "je" en "jij"
❌ NOOIT verboden woorden/zinnen gebruiken
❌ GEEN vaste templates of standaard structuren
❌ GEEN gethemede content - blijf bij het onderwerp
❌ GEEN actieve promotie van producten/links
❌ GEEN anchor tekst meer dan 1 keer gebruiken
❌ Geen AI-clichés
❌ Geen perfecte, gepolijste zinnen
❌ Geen marketing-taal

TOON:
- Professioneel maar niet stijf
- Praktisch en direct
- Alsof een expert advies geeft over dit specifieke onderwerp
- Geen verkoop-pitch, maar eerlijk advies
- Licht conversationeel zonder te casual te zijn
- Aangepast aan het onderwerp (formeel bij formele onderwerpen, toegankelijk bij toegankelijke onderwerpen)

TECHNISCHE EISEN:
- Woordenaantal: EXACT 500 woorden (±2 woorden toegestaan)
- Anchor teksten: Beide verplicht, PRECIES 1 KEER elk, SUBTIEL verweven
- H1: EXACT het onderwerp "{onderwerp}"
- Headings: Relevant voor het onderwerp, GEEN vaste templates, WEL met "H1: ", "H2: ", "H3: " prefix
- Conclusie: ALTIJD "H2: Conclusie" met hoofdletter C
- Alinea's: 2-4 zinnen per alinea
- Geen intro zoals "In dit artikel..." - begin direct met de kern

{extra_context}

Schrijf nu het artikel. Begin direct met de H1 titel: "H1: {onderwerp}".
ONTHOUD: ABSOLUUT GEEN "voordelen" of "voordeel" gebruiken!"""

# General AI writer prompt
GENERAL_ARTICLE_PROMPT = """Je bent een professionele Nederlandse contentschrijver. Je schrijft natuurlijke, menselijke teksten die NIET detecteerbaar zijn als AI-gegenereerd.

OPDRACHT:
Schrijf een artikel over: {onderwerp}

{word_count_instruction}

SCHRIJFSTIJL:
✅ Gebruik ALTIJD "je" en "jij" (NOOIT "u")
✅ Korte, pakkende zinnen
✅ Afwisselende zinslengte
✅ Directe aanspreking
✅ Natuurlijk en menselijk
✅ Professioneel maar toegankelijk
✅ Concrete voorbeelden

⚠️ VERBODEN WOORDEN EN ZINNEN - ZEER STRENG:
❌ ABSOLUUT VERBODEN: "voordelen" in ELKE vorm
❌ ABSOLUUT VERBODEN: "voordeel" in ELKE vorm
❌ ABSOLUUT VERBODEN: "voordelen van"
❌ ABSOLUUT VERBODEN: "voordeel van"
❌ ABSOLUUT VERBODEN: "Dat is best een opluchting, toch?"

✅ GEBRUIK IN PLAATS DAARVAN:
- pluspunten, sterke punten, wat het biedt, waarom het werkt, de kracht van, wat je ermee bereikt, de meerwaarde, het nut van

VERBODEN:
❌ NOOIT "u" gebruiken
❌ NOOIT "voordelen" of "voordeel" gebruiken
❌ NOOIT "Dat is best een opluchting, toch?" gebruiken
❌ Geen AI-clichés zoals "In de wereld van...", "Het is belangrijk om te..."
❌ Geen marketing-taal

STRUCTUUR:
- Gebruik H1 voor de hoofdtitel (markeer met "H1: ")
- Gebruik H2 voor hoofdsecties (markeer met "H2: ")
- Gebruik H3 voor subsecties indien nodig (markeer met "H3: ")
- Sluit af met "H2: Conclusie"

{extra_context}

Schrijf nu het artikel. ONTHOUD: ABSOLUUT GEEN "voordelen" of "voordeel" gebruiken!"""

def generate_topic(anchor1, anchor2, extra="", model="gpt-4o"):
    """Generate article topic based on anchor texts"""
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
            model=model,
            messages=[
                {"role": "system", "content": "Je bent een SEO expert die ALGEMENE artikel onderwerpen bedenkt. GEEN productnamen, merknamen, keywords, dubbele punten of jaartallen."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=100
        )
        
        topic = response.choices[0].message.content.strip()
        topic = topic.strip('"').strip("'")
        topic = topic.replace(':', '').replace('|', '').replace('-', ' ')
        topic = re.sub(r'\b20\d{2}\b', '', topic)
        topic = re.sub(r'\s+', ' ', topic).strip()
        
        return topic
    except Exception as e:
        print(f"OpenAI Topic Generation Error: {e}")
        raise

def generate_article(onderwerp, anchor1, url1, anchor2, url2, extra="", model="gpt-4o", max_retries=3):
    """Generate linkbuilding article with forbidden words check"""
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
    
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": f"Je bent een expert Nederlandse contentschrijver. H1 is EXACT '{onderwerp}'. ABSOLUUT VERBODEN: 'voordelen', 'voordeel' in ELKE vorm. Gebruik alternatieven zoals: pluspunten, sterke punten, wat het biedt, de meerwaarde."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.9,
                max_tokens=2000
            )
            
            article = response.choices[0].message.content.strip()
            
            # Check for forbidden words BEFORE formatting
            has_forbidden, found_phrases = check_forbidden_words(article)
            
            if has_forbidden:
                print(f"⚠️ Attempt {attempt + 1}: Found forbidden phrases: {found_phrases}")
                if attempt < max_retries - 1:
                    # Add stronger warning to prompt
                    prompt += f"\n\n⚠️ KRITIEK: Je gebruikte verboden woorden: {', '.join(found_phrases)}. Herschrijf ZONDER deze woorden!"
                    continue
                else:
                    # Last attempt - manually remove forbidden words
                    print("⚠️ Max retries reached. Manually removing forbidden words...")
                    article = re.sub(r'\bvoordelen\s+van\b', 'pluspunten van', article, flags=re.IGNORECASE)
                    article = re.sub(r'\bvoordeel\s+van\b', 'pluspunt van', article, flags=re.IGNORECASE)
                    article = re.sub(r'\bvoordelen\b', 'pluspunten', article, flags=re.IGNORECASE)
                    article = re.sub(r'\bvoordeel\b', 'pluspunt', article, flags=re.IGNORECASE)
                    article = re.sub(r'dat is best een opluchting,?\s*toch\??', 'dat is fijn om te weten', article, flags=re.IGNORECASE)
            
            article = re.sub(r'^H2:\s*conclusie\s*$', 'H2: Conclusie', article, flags=re.MULTILINE | re.IGNORECASE)
            article = format_article_html(article, anchor1, url1, anchor2, url2)
            
            print(f"✅ Article generated successfully (attempt {attempt + 1})")
            return article
            
        except Exception as e:
            print(f"OpenAI Error (attempt {attempt + 1}): {e}")
            if attempt == max_retries - 1:
                raise

def generate_general_article(onderwerp, word_count=500, extra="", model="gpt-4o", max_retries=3):
    """Generate general article without anchor texts with forbidden words check"""
    if not client:
        raise Exception("OpenAI API key not configured")
    
    word_count_instruction = f"Schrijf een artikel van ongeveer {word_count} woorden."
    
    extra_context = ""
    if extra:
        extra_context = f"\nEXTRA CONTEXT:\n{extra}"
    
    prompt = GENERAL_ARTICLE_PROMPT.format(
        onderwerp=onderwerp,
        word_count_instruction=word_count_instruction,
        extra_context=extra_context
    )
    
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "Je bent een expert Nederlandse contentschrijver. ABSOLUUT VERBODEN: 'voordelen', 'voordeel' in ELKE vorm. Gebruik alternatieven zoals: pluspunten, sterke punten, wat het biedt, de meerwaarde."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.9,
                max_tokens=3000
            )
            
            article = response.choices[0].message.content.strip()
            
            # Check for forbidden words BEFORE formatting
            has_forbidden, found_phrases = check_forbidden_words(article)
            
            if has_forbidden:
                print(f"⚠️ Attempt {attempt + 1}: Found forbidden phrases: {found_phrases}")
                if attempt < max_retries - 1:
                    prompt += f"\n\n⚠️ KRITIEK: Je gebruikte verboden woorden: {', '.join(found_phrases)}. Herschrijf ZONDER deze woorden!"
                    continue
                else:
                    # Last attempt - manually remove forbidden words
                    print("⚠️ Max retries reached. Manually removing forbidden words...")
                    article = re.sub(r'\bvoordelen\s+van\b', 'pluspunten van', article, flags=re.IGNORECASE)
                    article = re.sub(r'\bvoordeel\s+van\b', 'pluspunt van', article, flags=re.IGNORECASE)
                    article = re.sub(r'\bvoordelen\b', 'pluspunten', article, flags=re.IGNORECASE)
                    article = re.sub(r'\bvoordeel\b', 'pluspunt', article, flags=re.IGNORECASE)
                    article = re.sub(r'dat is best een opluchting,?\s*toch\??', 'dat is fijn om te weten', article, flags=re.IGNORECASE)
            
            article = re.sub(r'^H2:\s*conclusie\s*$', 'H2: Conclusie', article, flags=re.MULTILINE | re.IGNORECASE)
            article = format_article_html(article)
            
            print(f"✅ Article generated successfully (attempt {attempt + 1})")
            return article
            
        except Exception as e:
            print(f"OpenAI Error (attempt {attempt + 1}): {e}")
            if attempt == max_retries - 1:
                raise

def format_article_html(article, anchor1=None, url1=None, anchor2=None, url2=None):
    """Convert article with H1/H2/H3 markers to HTML"""
    
    # Replace heading markers with HTML tags
    article = re.sub(r'^H1:\s*(.+)$', r'<h1>\1</h1>', article, flags=re.MULTILINE)
    article = re.sub(r'^H2:\s*(.+)$', r'<h2>\1</h2>', article, flags=re.MULTILINE)
    article = re.sub(r'^H3:\s*(.+)$', r'<h3>\1</h3>', article, flags=re.MULTILINE)
    
    # Replace anchor texts with links if provided
    if anchor1 and url1:
        anchor1_escaped = re.escape(anchor1)
        article = re.sub(
            f'({anchor1_escaped})',
            f'<a href="{url1}" target="_blank">\\1</a>',
            article,
            count=1
        )
    
    if anchor2 and url2:
        anchor2_escaped = re.escape(anchor2)
        article = re.sub(
            f'({anchor2_escaped})',
            f'<a href="{url2}" target="_blank">\\1</a>',
            article,
            count=1
        )
    
    # Wrap paragraphs in <p> tags
    lines = article.split('\n')
    formatted_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if not line.startswith('<'):
            line = f'<p>{line}</p>'
        formatted_lines.append(line)
    
    return '\n'.join(formatted_lines)

def refine_article(article, topic, anchors, user_request, history=[], model="gpt-4o"):
    """Refine article based on user request"""
    if not client:
        raise Exception("OpenAI API key not configured")
    
    article_plain = re.sub(r'<[^>]+>', '', article)
    article_plain = article_plain.replace('<h1>', 'H1: ').replace('</h1>', '')
    article_plain = article_plain.replace('<h2>', 'H2: ').replace('</h2>', '')
    article_plain = article_plain.replace('<h3>', 'H3: ').replace('</h3>', '')
    
    system_prompt = f"""Je bent een expert Nederlandse contentschrijver die artikelen aanpast op basis van feedback.

HUIDIGE ARTIKEL ONDERWERP: {topic}

BELANGRIJKE REGELS:
- Gebruik ALTIJD "je" en "jij" (NOOIT "u")
- ABSOLUUT VERBODEN: "voordelen", "voordeel" in ELKE vorm
- ABSOLUUT VERBODEN: "Dat is best een opluchting, toch?"
- Gebruik alternatieven: pluspunten, sterke punten, wat het biedt, de meerwaarde
- Blijf rond de oorspronkelijke woordenaantal
- Schrijf natuurlijk en menselijk
- Geen AI-clichés

Pas het artikel aan volgens de vraag van de gebruiker."""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"HUIDIG ARTIKEL:\n\n{article_plain}\n\nAANPASSING GEVRAAGD:\n{user_request}\n\nGeef het volledige aangepaste artikel terug met H1:, H2:, H3: markers."}
    ]
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.8,
            max_tokens=3000
        )
        
        refined_article = response.choices[0].message.content.strip()
        
        # Check for forbidden words
        has_forbidden, found_phrases = check_forbidden_words(refined_article)
        if has_forbidden:
            print(f"⚠️ Refined article contains forbidden phrases: {found_phrases}. Cleaning...")
            refined_article = re.sub(r'\bvoordelen\s+van\b', 'pluspunten van', refined_article, flags=re.IGNORECASE)
            refined_article = re.sub(r'\bvoordeel\s+van\b', 'pluspunt van', refined_article, flags=re.IGNORECASE)
            refined_article = re.sub(r'\bvoordelen\b', 'pluspunten', refined_article, flags=re.IGNORECASE)
            refined_article = re.sub(r'\bvoordeel\b', 'pluspunt', refined_article, flags=re.IGNORECASE)
        
        refined_article = re.sub(r'^H2:\s*conclusie\s*$', 'H2: Conclusie', refined_article, flags=re.MULTILINE | re.IGNORECASE)
        
        # Convert to HTML with anchors if provided
        if anchors and 'anchor1' in anchors:
            refined_article = format_article_html(
                refined_article,
                anchors.get('anchor1'),
                anchors.get('url1'),
                anchors.get('anchor2'),
                anchors.get('url2')
            )
        else:
            refined_article = format_article_html(refined_article)
        
        return refined_article
    except Exception as e:
        print(f"OpenAI Refinement Error: {e}")
        raise

def fetch_wordpress_posts(site_url, username, app_password):
    """Fetch all posts from WordPress site for internal links"""
    posts = []
    page = 1
    per_page = 100
    
    while True:
        try:
            url = f"{site_url}/wp-json/wp/v2/posts"
            params = {
                'per_page': per_page,
                'page': page,
                'status': 'publish'
            }
            
            response = requests.get(
                url,
                params=params,
                auth=(username, app_password),
                timeout=30
            )
            
            if response.status_code != 200:
                break
            
            batch = response.json()
            if not batch:
                break
            
            for post in batch:
                posts.append({
                    'id': post['id'],
                    'title': post['title']['rendered'],
                    'url': post['link']
                })
            
            page += 1
            
            # Check if there are more pages
            total_pages = int(response.headers.get('X-WP-TotalPages', 1))
            if page > total_pages:
                break
                
        except Exception as e:
            print(f"Error fetching WordPress posts: {e}")
            break
    
    return posts

def check_originality(content):
    """Check content with Originality.AI"""
    if not ORIGINALITY_API_KEY:
        return {"error": "Originality.AI API key not configured"}
    
    try:
        url = "https://api.originality.ai/api/v1/scan/ai"
        headers = {
            "X-OAI-API-KEY": ORIGINALITY_API_KEY,
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        # Remove HTML tags for scanning
        text_content = re.sub(r'<[^>]+>', '', content)
        text_content = text_content.replace('\n', ' ').strip()
        
        payload = {
            "content": text_content,
            "title": "Article Scan",
            "aiModelVersion": "1"
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "ai_score": round(data.get('score', {}).get('ai', 0) * 100, 1),
                "human_score": round(data.get('score', {}).get('original', 0) * 100, 1)
            }
        else:
            return {"error": f"API Error: {response.status_code}"}
            
    except Exception as e:
        return {"error": str(e)}

def search_pixabay_images(query, per_page=5):
    """Search for images on Pixabay"""
    if not PIXABAY_API_KEY:
        return {"error": "Pixabay API key not configured"}
    
    try:
        url = "https://pixabay.com/api/"
        params = {
            "key": PIXABAY_API_KEY,
            "q": query,
            "image_type": "photo",
            "per_page": per_page,
            "safesearch": "true"
        }
        
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            images = []
            for hit in data.get('hits', []):
                images.append({
                    'id': hit['id'],
                    'url': hit['largeImageURL'],
                    'preview': hit['previewURL'],
                    'width': hit['imageWidth'],
                    'height': hit['imageHeight']
                })
            return {"success": True, "images": images}
        else:
            return {"error": f"API Error: {response.status_code}"}
            
    except Exception as e:
        return {"error": str(e)}

def generate_dalle_image(prompt):
    """Generate image using DALL-E 3"""
    if not client:
        raise Exception("OpenAI API key not configured")
    
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )
        
        image_url = response.data[0].url
        return {"success": True, "image_url": image_url}
        
    except Exception as e:
        return {"error": str(e)}

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/')
def index():
    """Serve the main HTML page"""
    return send_file('index.html')

@app.route('/api/generate-topic', methods=['POST'])
def api_generate_topic():
    """Generate article topic"""
    try:
        data = request.json
        anchor1 = data.get('anchor1', '').strip()
        anchor2 = data.get('anchor2', '').strip()
        extra = data.get('extra', '').strip()
        model = data.get('model', 'gpt-4o')
        
        if not anchor1 or not anchor2:
            return jsonify({"error": "Both anchor texts are required"}), 400
        
        topic = generate_topic(anchor1, anchor2, extra, model)
        return jsonify({"success": True, "topic": topic})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate-article', methods=['POST'])
def api_generate_article():
    """Generate linkbuilding article"""
    try:
        data = request.json
        onderwerp = data.get('onderwerp', '').strip()
        anchor1 = data.get('anchor1', '').strip()
        url1 = data.get('url1', '').strip()
        anchor2 = data.get('anchor2', '').strip()
        url2 = data.get('url2', '').strip()
        extra = data.get('extra', '').strip()
        model = data.get('model', 'gpt-4o')
        
        if not all([onderwerp, anchor1, url1, anchor2, url2]):
            return jsonify({"error": "All fields are required"}), 400
        
        article = generate_article(onderwerp, anchor1, url1, anchor2, url2, extra, model)
        
        # Count words
        text_content = re.sub(r'<[^>]+>', '', article)
        word_count = len(text_content.split())
        
        return jsonify({
            "success": True,
            "article": article,
            "word_count": word_count
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate-general-article', methods=['POST'])
def api_generate_general_article():
    """Generate general article"""
    try:
        data = request.json
        onderwerp = data.get('onderwerp', '').strip()
        word_count = int(data.get('word_count', 500))
        extra = data.get('extra', '').strip()
        model = data.get('model', 'gpt-4o')
        
        if not onderwerp:
            return jsonify({"error": "Topic is required"}), 400
        
        article = generate_general_article(onderwerp, word_count, extra, model)
        
        # Count words
        text_content = re.sub(r'<[^>]+>', '', article)
        actual_word_count = len(text_content.split())
        
        return jsonify({
            "success": True,
            "article": article,
            "word_count": actual_word_count
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/refine-article', methods=['POST'])
def api_refine_article():
    """Refine article based on user request"""
    try:
        data = request.json
        article = data.get('article', '').strip()
        topic = data.get('topic', '').strip()
        user_request = data.get('request', '').strip()
        anchors = data.get('anchors', {})
        model = data.get('model', 'gpt-4o')
        
        if not all([article, user_request]):
            return jsonify({"error": "Article and request are required"}), 400
        
        refined_article = refine_article(article, topic, anchors, user_request, model=model)
        
        # Count words
        text_content = re.sub(r'<[^>]+>', '', refined_article)
        word_count = len(text_content.split())
        
        return jsonify({
            "success": True,
            "article": refined_article,
            "word_count": word_count
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/check-originality', methods=['POST'])
def api_check_originality():
    """Check content originality"""
    try:
        data = request.json
        content = data.get('content', '').strip()
        
        if not content:
            return jsonify({"error": "Content is required"}), 400
        
        result = check_originality(content)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/search-images', methods=['POST'])
def api_search_images():
    """Search for images on Pixabay"""
    try:
        data = request.json
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({"error": "Search query is required"}), 400
        
        result = search_pixabay_images(query)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate-dalle-image', methods=['POST'])
def api_generate_dalle_image():
    """Generate image using DALL-E 3"""
    try:
        data = request.json
        prompt = data.get('prompt', '').strip()
        
        if not prompt:
            return jsonify({"error": "Prompt is required"}), 400
        
        result = generate_dalle_image(prompt)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============================================================================
# ARTICLE STORAGE ENDPOINTS
# ============================================================================

@app.route('/api/articles', methods=['GET'])
def get_articles():
    """Get all saved articles"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM articles 
            ORDER BY created_at DESC
        ''')
        
        articles = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({"success": True, "articles": articles})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/articles/<int:article_id>', methods=['GET'])
def get_article(article_id):
    """Get specific article"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM articles WHERE id = ?', (article_id,))
        article = cursor.fetchone()
        conn.close()
        
        if article:
            return jsonify({"success": True, "article": dict(article)})
        else:
            return jsonify({"error": "Article not found"}), 404
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/articles', methods=['POST'])
def save_article():
    """Save new article"""
    try:
        data = request.json
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Extract text content
        content_html = data.get('content_html', '')
        content_text = re.sub(r'<[^>]+>', '', content_html)
        word_count = len(content_text.split())
        
        cursor.execute('''
            INSERT INTO articles (
                title, content_html, content_text, article_type,
                anchor1, url1, anchor2, url2,
                word_count, human_score, ai_score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('title', ''),
            content_html,
            content_text,
            data.get('article_type', 'linkbuilding'),
            data.get('anchor1'),
            data.get('url1'),
            data.get('anchor2'),
            data.get('url2'),
            word_count,
            data.get('human_score'),
            data.get('ai_score')
        ))
        
        article_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({"success": True, "article_id": article_id})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/articles/<int:article_id>', methods=['PUT'])
def update_article(article_id):
    """Update existing article"""
    try:
        data = request.json
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Extract text content
        content_html = data.get('content_html', '')
        content_text = re.sub(r'<[^>]+>', '', content_html)
        word_count = len(content_text.split())
        
        cursor.execute('''
            UPDATE articles SET
                title = ?,
                content_html = ?,
                content_text = ?,
                anchor1 = ?,
                url1 = ?,
                anchor2 = ?,
                url2 = ?,
                word_count = ?,
                human_score = ?,
                ai_score = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (
            data.get('title', ''),
            content_html,
            content_text,
            data.get('anchor1'),
            data.get('url1'),
            data.get('anchor2'),
            data.get('url2'),
            word_count,
            data.get('human_score'),
            data.get('ai_score'),
            article_id
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({"success": True})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/articles/<int:article_id>', methods=['DELETE'])
def delete_article(article_id):
    """Delete article"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM articles WHERE id = ?', (article_id,))
        
        conn.commit()
        conn.close()
        
        return jsonify({"success": True})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============================================================================
# WORDPRESS SITES MANAGEMENT
# ============================================================================

@app.route('/api/wordpress-sites', methods=['GET'])
def get_wordpress_sites():
    """Get all WordPress sites"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, site_name, site_url, username FROM wordpress_sites ORDER BY site_name')
        sites = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({"success": True, "sites": sites})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/wordpress-sites', methods=['POST'])
def add_wordpress_site():
    """Add new WordPress site"""
    try:
        data = request.json
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO wordpress_sites (site_name, site_url, username, app_password)
            VALUES (?, ?, ?, ?)
        ''', (
            data.get('site_name'),
            data.get('site_url'),
            data.get('username'),
            data.get('app_password')
        ))
        
        site_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({"success": True, "site_id": site_id})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/wordpress-sites/<int:site_id>', methods=['DELETE'])
def delete_wordpress_site(site_id):
    """Delete WordPress site"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM wordpress_sites WHERE id = ?', (site_id,))
        
        conn.commit()
        conn.close()
        
        return jsonify({"success": True})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/wordpress-sites/<int:site_id>/posts', methods=['GET'])
def get_wordpress_posts(site_id):
    """Fetch posts from WordPress site"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM wordpress_sites WHERE id = ?', (site_id,))
        site = cursor.fetchone()
        conn.close()
        
        if not site:
            return jsonify({"error": "Site not found"}), 404
        
        posts = fetch_wordpress_posts(site['site_url'], site['username'], site['app_password'])
        
        return jsonify({"success": True, "posts": posts})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============================================================================
# INTERNAL & AFFILIATE LINKS MANAGEMENT
# ============================================================================

@app.route('/api/wordpress-sites/<int:site_id>/internal-links', methods=['GET'])
def get_internal_links(site_id):
    """Get internal links for a site"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM internal_links WHERE site_id = ? ORDER BY anchor_text', (site_id,))
        links = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({"success": True, "links": links})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/wordpress-sites/<int:site_id>/internal-links', methods=['POST'])
def add_internal_link(site_id):
    """Add internal link"""
    try:
        data = request.json
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO internal_links (site_id, anchor_text, url)
            VALUES (?, ?, ?)
        ''', (site_id, data.get('anchor_text'), data.get('url')))
        
        link_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({"success": True, "link_id": link_id})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/internal-links/<int:link_id>', methods=['DELETE'])
def delete_internal_link(link_id):
    """Delete internal link"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM internal_links WHERE id = ?', (link_id,))
        
        conn.commit()
        conn.close()
        
        return jsonify({"success": True})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/wordpress-sites/<int:site_id>/affiliate-links', methods=['GET'])
def get_affiliate_links(site_id):
    """Get affiliate links for a site"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM affiliate_links WHERE site_id = ? ORDER BY anchor_text', (site_id,))
        links = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({"success": True, "links": links})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/wordpress-sites/<int:site_id>/affiliate-links', methods=['POST'])
def add_affiliate_link(site_id):
    """Add affiliate link"""
    try:
        data = request.json
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO affiliate_links (site_id, anchor_text, url)
            VALUES (?, ?, ?)
        ''', (site_id, data.get('anchor_text'), data.get('url')))
        
        link_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({"success": True, "link_id": link_id})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/affiliate-links/<int:link_id>', methods=['DELETE'])
def delete_affiliate_link(link_id):
    """Delete affiliate link"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM affiliate_links WHERE id = ?', (link_id,))
        
        conn.commit()
        conn.close()
        
        return jsonify({"success": True})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
