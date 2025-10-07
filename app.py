#!/usr/bin/env python3
"""
Writgo Academy Content Generator
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

# FORBIDDEN PHRASES - Updated list
FORBIDDEN_PHRASES = [
    "voordelen van",
    "voordelen",
    "dat is best een opluchting, toch?"
]

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

# Article generation prompt - UPDATED with forbidden phrases
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

VERBODEN WOORDEN EN ZINNEN:
❌ NOOIT "voordelen" gebruiken
❌ NOOIT "voordelen van" gebruiken
❌ NOOIT "Dat is best een opluchting, toch?" gebruiken
❌ Gebruik alternatieven: pluspunten, sterke punten, wat het biedt, waarom het werkt, de kracht van, wat je ermee bereikt, etc.

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

Schrijf nu het artikel. Begin direct met de H1 titel: "H1: {onderwerp}"."""

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

VERBODEN:
❌ NOOIT "u" gebruiken
❌ NOOIT "voordelen" gebruiken
❌ NOOIT "voordelen van" gebruiken
❌ NOOIT "Dat is best een opluchting, toch?" gebruiken
❌ Geen AI-clichés zoals "In de wereld van...", "Het is belangrijk om te..."
❌ Geen marketing-taal

STRUCTUUR:
- Gebruik H1 voor de hoofdtitel (markeer met "H1: ")
- Gebruik H2 voor hoofdsecties (markeer met "H2: ")
- Gebruik H3 voor subsecties indien nodig (markeer met "H3: ")
- Sluit af met "H2: Conclusie"

{extra_context}

Schrijf nu het artikel."""

def generate_topic(anchor1, anchor2, extra=""):
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
            model="gpt-4o",
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

def generate_article(onderwerp, anchor1, url1, anchor2, url2, extra=""):
    """Generate linkbuilding article"""
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
                {"role": "system", "content": f"Je bent een expert Nederlandse contentschrijver. H1 is EXACT '{onderwerp}'. NOOIT verboden woorden/zinnen gebruiken."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.9,
            max_tokens=2000
        )
        
        article = response.choices[0].message.content.strip()
        article = re.sub(r'^H2:\s*conclusie\s*$', 'H2: Conclusie', article, flags=re.MULTILINE | re.IGNORECASE)
        article = format_article_html(article, anchor1, url1, anchor2, url2)
        
        return article
    except Exception as e:
        print(f"OpenAI Error: {e}")
        raise

def generate_general_article(onderwerp, word_count=500, extra=""):
    """Generate general article without anchor texts"""
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
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Je bent een expert Nederlandse contentschrijver. NOOIT verboden woorden/zinnen gebruiken."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.9,
            max_tokens=3000
        )
        
        article = response.choices[0].message.content.strip()
        article = re.sub(r'^H2:\s*conclusie\s*$', 'H2: Conclusie', article, flags=re.MULTILINE | re.IGNORECASE)
        article = format_article_html(article)
        
        return article
    except Exception as e:
        print(f"OpenAI Error: {e}")
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

def refine_article(article, topic, anchors, user_request, history=[]):
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
- NOOIT verboden woorden/zinnen gebruiken: {', '.join(FORBIDDEN_PHRASES)}
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
            model="gpt-4o",
            messages=messages,
            temperature=0.8,
            max_tokens=3000
        )
        
        refined_article = response.choices[0].message.content.strip()
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

def check_originality(text):
    """Check originality using Originality.AI"""
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
        
        scan_url = None
        if 'public_link' in data:
            scan_url = data['public_link']
        elif 'id' in data:
            scan_url = f"https://app.originality.ai/scan/{data['id']}"
        
        print(f"✅ Originality check: AI={ai_score}%, Human={human_score}%")
        
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
    text = re.sub(r'<[^>]+>', '', text)
    words = text.split()
    return len(words)

# ============= ROUTES =============

@app.route('/')
def index():
    """Serve the HTML frontend"""
    return send_file('index.html')

@app.route('/generate-linkbuilding', methods=['POST'])
def generate_linkbuilding_endpoint():
    """Generate linkbuilding article"""
    try:
        data = request.json
        
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
        
        print(f"Generating topic for anchors: {anchor1}, {anchor2}")
        onderwerp = generate_topic(anchor1, anchor2, extra)
        print(f"Generated topic: {onderwerp}")
        
        print(f"Generating article for: {onderwerp}")
        article = generate_article(onderwerp, anchor1, url1, anchor2, url2, extra)
        
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
            'word_count': word_count
        })
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/generate-general', methods=['POST'])
def generate_general_endpoint():
    """Generate general article"""
    try:
        data = request.json
        
        onderwerp = data.get('topic')
        word_count = data.get('word_count', 500)
        extra = data.get('extra', '')
        
        if not onderwerp:
            return jsonify({
                'success': False,
                'error': 'Onderwerp is verplicht'
            }), 400
        
        print(f"Generating general article: {onderwerp}")
        article = generate_general_article(onderwerp, word_count, extra)
        
        article_text = re.sub(r'<[^>]+>', '', article)
        article_text = article_text.replace('</h1>', '\n').replace('</h2>', '\n').replace('</h3>', '\n').replace('</p>', '\n\n')
        article_text = re.sub(r'\n\n+', '\n\n', article_text).strip()
        
        word_count_actual = count_words(article)
        print(f"Article generated: {word_count_actual} words")
        
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
            'word_count': word_count_actual
        })
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/refine-article', methods=['POST'])
def refine_article_endpoint():
    """Refine article based on user request"""
    try:
        data = request.json
        
        article = data.get('article')
        instruction = data.get('instruction')
        topic = data.get('topic', 'Artikel')
        anchors = data.get('anchors', {})
        
        if not all([article, instruction]):
            return jsonify({
                'success': False,
                'error': 'Ontbrekende gegevens'
            }), 400
        
        print(f"Refining article: {instruction}")
        refined_article = refine_article(article, topic, anchors, instruction, [])
        
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
            'word_count': word_count
        })
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============= ARTICLE STORAGE =============

@app.route('/save-article', methods=['POST'])
def save_article():
    """Save article to database"""
    try:
        data = request.json
        
        title = data.get('title')
        content_html = data.get('content_html')
        content_text = data.get('content_text')
        article_type = data.get('article_type', 'linkbuilding')
        anchor1 = data.get('anchor1', '')
        url1 = data.get('url1', '')
        anchor2 = data.get('anchor2', '')
        url2 = data.get('url2', '')
        word_count = data.get('word_count', 0)
        human_score = data.get('human_score', 0)
        ai_score = data.get('ai_score', 0)
        
        if not all([title, content_html, content_text]):
            return jsonify({
                'success': False,
                'error': 'Titel en content zijn verplicht'
            }), 400
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO articles (title, content_html, content_text, article_type, anchor1, url1, anchor2, url2, word_count, human_score, ai_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (title, content_html, content_text, article_type, anchor1, url1, anchor2, url2, word_count, human_score, ai_score))
        conn.commit()
        article_id = cursor.lastrowid
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Artikel opgeslagen!',
            'article_id': article_id
        })
        
    except Exception as e:
        print(f"Error saving article: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/get-articles', methods=['GET'])
def get_articles():
    """Get all saved articles"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM articles ORDER BY created_at DESC')
        rows = cursor.fetchall()
        conn.close()
        
        articles = []
        for row in rows:
            articles.append({
                'id': row['id'],
                'title': row['title'],
                'content_html': row['content_html'],
                'content_text': row['content_text'],
                'article_type': row['article_type'],
                'anchor1': row['anchor1'],
                'url1': row['url1'],
                'anchor2': row['anchor2'],
                'url2': row['url2'],
                'word_count': row['word_count'],
                'human_score': row['human_score'],
                'ai_score': row['ai_score'],
                'created_at': row['created_at'],
                'updated_at': row['updated_at']
            })
        
        return jsonify({
            'success': True,
            'articles': articles
        })
        
    except Exception as e:
        print(f"Error getting articles: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/delete-article/<int:article_id>', methods=['DELETE'])
def delete_article(article_id):
    """Delete an article"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM articles WHERE id = ?', (article_id,))
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Artikel verwijderd!'
        })
        
    except Exception as e:
        print(f"Error deleting article: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============= WORDPRESS SITES =============

@app.route('/wordpress-sites', methods=['GET'])
def get_wordpress_sites():
    """Get all WordPress sites"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM wordpress_sites ORDER BY site_name')
        rows = cursor.fetchall()
        conn.close()
        
        sites = []
        for row in rows:
            sites.append({
                'id': row['id'],
                'site_name': row['site_name'],
                'site_url': row['site_url'],
                'username': row['username'],
                'created_at': row['created_at']
            })
        
        return jsonify({
            'success': True,
            'sites': sites
        })
        
    except Exception as e:
        print(f"Error getting sites: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/wordpress-sites', methods=['POST'])
def add_wordpress_site():
    """Add new WordPress site"""
    try:
        data = request.json
        
        site_name = data.get('site_name')
        site_url = data.get('site_url')
        username = data.get('username')
        app_password = data.get('app_password')
        
        if not all([site_name, site_url, username, app_password]):
            return jsonify({
                'success': False,
                'error': 'Alle velden zijn verplicht'
            }), 400
        
        # Ensure site_url ends with /
        if not site_url.endswith('/'):
            site_url += '/'
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO wordpress_sites (site_name, site_url, username, app_password)
            VALUES (?, ?, ?, ?)
        ''', (site_name, site_url, username, app_password))
        conn.commit()
        site_id = cursor.lastrowid
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'WordPress site toegevoegd!',
            'site_id': site_id
        })
        
    except sqlite3.IntegrityError:
        return jsonify({
            'success': False,
            'error': 'Deze site naam bestaat al'
        }), 400
    except Exception as e:
        print(f"Error adding site: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/wordpress-sites/<int:site_id>', methods=['DELETE'])
def delete_wordpress_site(site_id):
    """Delete WordPress site"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM wordpress_sites WHERE id = ?', (site_id,))
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'WordPress site verwijderd!'
        })
        
    except Exception as e:
        print(f"Error deleting site: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============= INTERNAL LINKS =============

@app.route('/internal-links/<int:site_id>', methods=['GET'])
def get_internal_links(site_id):
    """Get internal links for a site"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM internal_links WHERE site_id = ? ORDER BY anchor_text', (site_id,))
        rows = cursor.fetchall()
        conn.close()
        
        links = []
        for row in rows:
            links.append({
                'id': row['id'],
                'anchor_text': row['anchor_text'],
                'url': row['url']
            })
        
        return jsonify({
            'success': True,
            'links': links
        })
        
    except Exception as e:
        print(f"Error getting internal links: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/internal-links/<int:site_id>', methods=['POST'])
def add_internal_link(site_id):
    """Add internal link for a site"""
    try:
        data = request.json
        
        anchor_text = data.get('anchor_text')
        url = data.get('url')
        
        if not all([anchor_text, url]):
            return jsonify({
                'success': False,
                'error': 'Anchor tekst en URL zijn verplicht'
            }), 400
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO internal_links (site_id, anchor_text, url)
            VALUES (?, ?, ?)
        ''', (site_id, anchor_text, url))
        conn.commit()
        link_id = cursor.lastrowid
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Interne link toegevoegd!',
            'link_id': link_id
        })
        
    except Exception as e:
        print(f"Error adding internal link: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/internal-links/<int:link_id>', methods=['DELETE'])
def delete_internal_link(link_id):
    """Delete internal link"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM internal_links WHERE id = ?', (link_id,))
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Interne link verwijderd!'
        })
        
    except Exception as e:
        print(f"Error deleting internal link: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============= AFFILIATE LINKS =============

@app.route('/affiliate-links/<int:site_id>', methods=['GET'])
def get_affiliate_links(site_id):
    """Get affiliate links for a site"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM affiliate_links WHERE site_id = ? ORDER BY anchor_text', (site_id,))
        rows = cursor.fetchall()
        conn.close()
        
        links = []
        for row in rows:
            links.append({
                'id': row['id'],
                'anchor_text': row['anchor_text'],
                'url': row['url']
            })
        
        return jsonify({
            'success': True,
            'links': links
        })
        
    except Exception as e:
        print(f"Error getting affiliate links: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/affiliate-links/<int:site_id>', methods=['POST'])
def add_affiliate_link(site_id):
    """Add affiliate link for a site"""
    try:
        data = request.json
        
        anchor_text = data.get('anchor_text')
        url = data.get('url')
        
        if not all([anchor_text, url]):
            return jsonify({
                'success': False,
                'error': 'Anchor tekst en URL zijn verplicht'
            }), 400
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO affiliate_links (site_id, anchor_text, url)
            VALUES (?, ?, ?)
        ''', (site_id, anchor_text, url))
        conn.commit()
        link_id = cursor.lastrowid
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Affiliate link toegevoegd!',
            'link_id': link_id
        })
        
    except Exception as e:
        print(f"Error adding affiliate link: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/affiliate-links/<int:link_id>', methods=['DELETE'])
def delete_affiliate_link(link_id):
    """Delete affiliate link"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM affiliate_links WHERE id = ?', (link_id,))
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Affiliate link verwijderd!'
        })
        
    except Exception as e:
        print(f"Error deleting affiliate link: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============= WORDPRESS PUBLISHING =============

@app.route('/publish-to-wordpress', methods=['POST'])
def publish_to_wordpress():
    """Publish article to WordPress"""
    try:
        data = request.json
        
        site_id = data.get('site_id')
        title = data.get('title')
        content = data.get('content')
        status = data.get('status', 'draft')  # draft or publish
        
        if not all([site_id, title, content]):
            return jsonify({
                'success': False,
                'error': 'Site, titel en content zijn verplicht'
            }), 400
        
        # Get site credentials
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM wordpress_sites WHERE id = ?', (site_id,))
        site = cursor.fetchone()
        conn.close()
        
        if not site:
            return jsonify({
                'success': False,
                'error': 'WordPress site niet gevonden'
            }), 404
        
        # Publish to WordPress
        wp_url = f"{site['site_url']}wp-json/wp/v2/posts"
        
        auth = (site['username'], site['app_password'])
        
        post_data = {
            'title': title,
            'content': content,
            'status': status
        }
        
        response = requests.post(wp_url, json=post_data, auth=auth)
        response.raise_for_status()
        
        post_info = response.json()
        
        return jsonify({
            'success': True,
            'message': f'Artikel gepubliceerd als {status}!',
            'post_id': post_info.get('id'),
            'post_url': post_info.get('link')
        })
        
    except requests.exceptions.HTTPError as e:
        print(f"WordPress API Error: {e}")
        return jsonify({
            'success': False,
            'error': f'WordPress fout: {str(e)}'
        }), 500
    except Exception as e:
        print(f"Error publishing to WordPress: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("🚀 Starting Writgo Academy Content Generator...")
    print("🎨 BRANDING: Writgo Academy kleuren")
    print("📝 LINKBUILDING: Artikelen met anchor teksten")
    print("✍️  ALGEMENE SCHRIJVER: Vrije artikelen")
    print("🌐 WORDPRESS: Multi-site beheer met app wachtwoorden")
    print("🔗 INTERNE LINKS: Per website beheren")
    print("💰 AFFILIATE LINKS: Per website beheren")
    print("🚫 VERBODEN: voordelen, voordelen van, 'Dat is best een opluchting, toch?'")
    print(f"📍 Running on port: {port}")
    print("")
    if not client:
        print("⚠️  WARNING: OpenAI API key not configured!")
    app.run(host='0.0.0.0', port=port, debug=False)
