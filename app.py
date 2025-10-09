#!/usr/bin/env python3
"""
WritgoAI Content Generator v21
Multi-feature content creation platform with WordPress integration
Enhanced with extra elements: tables, FAQ, bold text, Pixabay images, DALL-E images, YouTube videos

NEW IN V21:
- FIXED: Enforced word count with retry mechanism (minimum 90% of target)
- FIXED: Strip markdown code blocks (```html, ```markdown, etc.)
- FIXED: Stricter whitespace cleaning (max 1 blank line)
- FIXED: Mandatory list/table/FAQ when requested
- HTML output instead of markdown (proper <h2>, <h3> tags for WordPress blocks)
- 1 image per 500 words (configurable)
- Maximum 1 blank line between paragraphs
- WordPress sitemap integration
- Improved Pixabay keyword generation (more relevant images)
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
from deep_translator import GoogleTranslator
from urllib.parse import urljoin, urlparse
import xml.etree.ElementTree as ET
try:
    import anthropic
except ImportError:
    anthropic = None

# Import backend utilities
from backend_utils import find_sitemap, extract_internal_links, detect_affiliate_links, fetch_sitemap_urls

app = Flask(__name__)
CORS(app)

# Error handlers
@app.errorhandler(400)
def bad_request(error):
    """Handle bad request errors"""
    return jsonify({
        "success": False,
        "error": "Bad request - Invalid JSON or missing required fields"
    }), 400

@app.errorhandler(404)
def not_found(error):
    """Handle not found errors"""
    return jsonify({
        "success": False,
        "error": "Endpoint not found"
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle internal server errors"""
    import traceback
    error_details = str(error)
    print(f"❌ Internal Server Error: {error_details}")
    print(traceback.format_exc())
    return jsonify({
        "success": False,
        "error": "Internal server error",
        "details": error_details
    }), 500

@app.errorhandler(Exception)
def handle_exception(error):
    """Handle all unhandled exceptions"""
    import traceback
    error_details = str(error)
    print(f"❌ Unhandled Exception: {error_details}")
    print(traceback.format_exc())
    return jsonify({
        "success": False,
        "error": "An unexpected error occurred",
        "details": error_details
    }), 500

@app.after_request
def after_request(response):
    """Ensure JSON responses have correct Content-Type"""
    if response.status_code >= 200 and response.status_code < 300:
        if not response.content_type or 'text/html' in response.content_type:
            if request.path.startswith('/api/'):
                response.content_type = 'application/json'
    return response

# Database setup
DB_PATH = 'writgo_content.db'

def init_db():
    """Initialize SQLite database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
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
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS wordpress_sites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            site_name TEXT NOT NULL UNIQUE,
            site_url TEXT NOT NULL,
            username TEXT NOT NULL,
            app_password TEXT NOT NULL,
            sitemap_url TEXT,
            context TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
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
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS knowledge_base (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            site_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            content TEXT NOT NULL,
            file_type TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (site_id) REFERENCES wordpress_sites(id) ON DELETE CASCADE
        )
    ''')
    
    try:
        cursor.execute('ALTER TABLE wordpress_sites ADD COLUMN sitemap_url TEXT')
    except sqlite3.OperationalError:
        pass
    
    try:
        cursor.execute('ALTER TABLE wordpress_sites ADD COLUMN context TEXT')
    except sqlite3.OperationalError:
        pass
    
    conn.commit()
    conn.close()
    print("✅ Database initialized")

init_db()

# Load API keys
def load_api_keys():
    """Load API keys from environment variables or secrets file"""
    keys = {
        'openai': None,
        'anthropic': None,
        'originality': None,
        'pixabay': None,
        'perplexity': None
    }
    
    keys['openai'] = os.getenv('OPENAI_API_KEY')
    keys['anthropic'] = os.getenv('ANTHROPIC_API_KEY')
    keys['originality'] = os.getenv('ORIGINALITY_API_KEY')
    keys['pixabay'] = os.getenv('PIXABAY_API_KEY')
    keys['perplexity'] = os.getenv('PERPLEXITY_API_KEY')
    
    secrets_path = '/home/ubuntu/.config/abacusai_auth_secrets.json'
    if os.path.exists(secrets_path):
        try:
            with open(secrets_path, 'r') as f:
                secrets = json.load(f)
            
            if not keys['openai'] and 'openai' in secrets and 'secrets' in secrets['openai']:
                if 'api_key' in secrets['openai']['secrets']:
                    keys['openai'] = secrets['openai']['secrets']['api_key']['value']
            
            if not keys['anthropic'] and 'anthropic' in secrets and 'secrets' in secrets['anthropic']:
                if 'api_key' in secrets['anthropic']['secrets']:
                    keys['anthropic'] = secrets['anthropic']['secrets']['api_key']['value']
            
            if not keys['originality'] and 'originality.ai' in secrets and 'secrets' in secrets['originality.ai']:
                if 'api_key' in secrets['originality.ai']['secrets']:
                    keys['originality'] = secrets['originality.ai']['secrets']['api_key']['value']
            
            if not keys['pixabay'] and 'pixabay' in secrets and 'secrets' in secrets['pixabay']:
                if 'api_key' in secrets['pixabay']['secrets']:
                    keys['pixabay'] = secrets['pixabay']['secrets']['api_key']['value']
            
            if not keys['perplexity'] and 'perplexity' in secrets and 'secrets' in secrets['perplexity']:
                if 'api_key' in secrets['perplexity']['secrets']:
                    keys['perplexity'] = secrets['perplexity']['secrets']['api_key']['value']
        except Exception as e:
            print(f"⚠️  Error loading API keys from secrets file: {e}")
    
    return keys

api_keys = load_api_keys()
OPENAI_API_KEY = api_keys['openai']
ANTHROPIC_API_KEY = api_keys['anthropic']
ORIGINALITY_API_KEY = api_keys['originality']
PIXABAY_API_KEY = api_keys['pixabay']
PERPLEXITY_API_KEY = api_keys['perplexity']

# Initialize OpenAI client
client = None
if OPENAI_API_KEY:
    http_client = httpx.Client(timeout=120.0, follow_redirects=True)
    client = OpenAI(api_key=OPENAI_API_KEY, http_client=http_client)
    print("✅ OpenAI API key loaded")
else:
    print("⚠️  OpenAI API key not found")

# Initialize Anthropic client
anthropic_client = None
if ANTHROPIC_API_KEY:
    try:
        import anthropic
        anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        print("✅ Anthropic API key loaded")
    except ImportError:
        print("⚠️  Anthropic library not installed")
else:
    print("⚠️  Anthropic API key not found")

if ORIGINALITY_API_KEY:
    print("✅ Originality.AI API key loaded")
else:
    print("⚠️  Originality.AI API key not found")

if PIXABAY_API_KEY:
    print("✅ Pixabay API key loaded")
else:
    print("⚠️  Pixabay API key not found")

if PERPLEXITY_API_KEY:
    print("✅ Perplexity API key loaded")
else:
    print("⚠️  Perplexity API key not found")

# FORBIDDEN PHRASES
FORBIDDEN_PHRASES = [
    "dat is best een opluchting, toch?",
    "dat is best een opluchting toch",
    "dat is best een opluchting"
]

def check_forbidden_words(text):
    """Check if text contains forbidden phrases"""
    text_lower = text.lower()
    found_phrases = []
    
    for phrase in FORBIDDEN_PHRASES:
        pattern = r'\b' + re.escape(phrase.lower()) + r'\b'
        if re.search(pattern, text_lower):
            found_phrases.append(phrase)
    
    return (len(found_phrases) > 0, found_phrases)

def to_sentence_case(text):
    """Convert text to sentence case"""
    if not text:
        return text
    return text[0].upper() + text[1:]

def call_openai_with_correct_params(model, messages, temperature=0.9, max_tokens=2000):
    """Call OpenAI API with correct parameters based on model"""
    if model in ["gpt-5", "o1-preview", "o1-mini"]:
        return client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_completion_tokens=max_tokens
        )
    else:
        return client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )

def clean_markdown_blocks(text):
    """
    Remove markdown code block markers from text
    Strips ```html, ```markdown, ``` at beginning/end
    """
    # Remove code block markers at start
    text = re.sub(r'^```(?:html|markdown|md)?\s*\n?', '', text, flags=re.MULTILINE)
    
    # Remove code block markers at end
    text = re.sub(r'\n?```\s*$', '', text, flags=re.MULTILINE)
    
    # Remove any remaining standalone ``` markers
    text = re.sub(r'^```\s*$', '', text, flags=re.MULTILINE)
    
    return text.strip()

def normalize_whitespace(text):
    """
    Aggressive whitespace cleaning
    - Max 1 blank line between elements
    - Remove trailing/leading whitespace
    - Consistent line breaks
    """
    # Remove trailing whitespace from each line
    lines = text.split('\n')
    lines = [line.rstrip() for line in lines]
    
    # Join and collapse multiple blank lines to max 1
    text = '\n'.join(lines)
    
    # Replace 3+ newlines with exactly 2 (1 blank line)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Remove leading/trailing whitespace from entire text
    text = text.strip()
    
    return text

def count_words(text):
    """Count words in text (excluding HTML tags)"""
    # Remove HTML tags
    text_only = re.sub(r'<[^>]+>', '', text)
    # Count words
    words = text_only.split()
    return len(words)

def enforce_word_count(article, target_word_count, min_percentage=0.95):
    """
    Validate that article meets minimum word count requirement
    Returns (is_valid, actual_count, message)
    
    Default min_percentage is 0.95 (95%) to ensure articles are close to target length.
    For 1500 words target, minimum is 1425 words.
    """
    actual_count = count_words(article)
    min_required = int(target_word_count * min_percentage)
    
    is_valid = actual_count >= min_required
    
    if is_valid:
        message = f"✅ Word count OK: {actual_count}/{target_word_count} words ({actual_count/target_word_count*100:.1f}%)"
    else:
        message = f"❌ Word count too low: {actual_count}/{target_word_count} words (minimum {min_required} required, {min_percentage*100:.0f}% threshold)"
    
    return is_valid, actual_count, message

def enforce_options(article, elements):
    """
    Validate that requested options are present in article
    Returns (is_valid, missing_elements)
    """
    missing = []
    
    if elements.get('include_lists'):
        if not re.search(r'<ul>.*?</ul>', article, re.DOTALL):
            missing.append('lijst')
    
    if elements.get('include_tables'):
        if not re.search(r'<table>.*?</table>', article, re.DOTALL):
            missing.append('tabel')
    
    if elements.get('include_faq'):
        if not re.search(r'<h2>Veelgestelde vragen</h2>', article, re.IGNORECASE):
            missing.append('FAQ sectie')
    
    is_valid = len(missing) == 0
    
    return is_valid, missing

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

# Article generation prompt - UPDATED for HTML output
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
- 1x <h1> (hoofdtitel) - gebruik EXACT het onderwerp: "{onderwerp}"
- 3x <h2> (hoofdsecties)
- 2x <h3> (subsecties)
- Intro alinea (zonder heading)
- Conclusie sectie (met <h2>Conclusie</h2>)

ANCHOR TEKSTEN (SUBTIEL VERWERKEN):
Verwerk deze twee anchor teksten SUBTIEL en NATUURLIJK in de lopende tekst:
1. "{anchor1}" → link naar: {url1}
2. "{anchor2}" → link naar: {url2}

KRITIEKE REGELS VOOR ANCHOR TEKSTEN:
✅ Gebruik elke anchor tekst PRECIES 1 KEER in het hele artikel
✅ Noem ze SUBTIEL in de lopende tekst, niet prominent
✅ GEEN actieve promotie of verkoop-taal
✅ Gewoon terloops noemen als voorbeeld of optie

HEADINGS - ZEER BELANGRIJK (HTML FORMAT):
✅ <h1>: Gebruik EXACT het onderwerp "{onderwerp}"
✅ <h2> en <h3>: Gebruik Sentence case - alleen eerste letter hoofdletter
✅ Voorbeeld GOED: <h2>Dit is een heading</h2> (niet <h2>Dit Is Een Heading</h2>)
✅ <h2> en <h3>: Maak deze RELEVANT voor het specifieke onderwerp
✅ <h2> en <h3>: GEEN vaste templates of standaard koppen
✅ <h2> en <h3>: Pas aan bij de inhoud en het onderwerp
✅ Laatste <h2> moet zijn: <h2>Conclusie</h2> (met hoofdletter C)
✅ Gebruik ECHTE HTML tags: <h1>, <h2>, <h3> (NIET ## of ###)

⚠️ VERBODEN WOORDEN EN ZINNEN - ZEER STRENG:
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
- Aangepast aan het onderwerp

TECHNISCHE EISEN:
- Woordenaantal: EXACT 500 woorden (±2 woorden toegestaan)
- Anchor teksten: Beide verplicht, PRECIES 1 KEER elk, SUBTIEL verweven
- <h1>: EXACT het onderwerp "{onderwerp}"
- Headings: Sentence case, relevant voor het onderwerp, GEEN vaste templates, gebruik ECHTE HTML tags
- Conclusie: ALTIJD <h2>Conclusie</h2> met hoofdletter C
- Alinea's: 2-4 zinnen per alinea, gewrappt in <p> tags
- Geen intro zoals "In dit artikel..." - begin direct met de kern

{extra_context}

Schrijf nu het artikel. Begin direct met de <h1> titel: <h1>{onderwerp}</h1>.
ONTHOUD: Gebruik ECHTE HTML tags (<h1>, <h2>, <h3>, <p>) en Sentence case voor headings!
GEEN markdown code blocks - schrijf direct HTML zonder ``` markers!"""

# General AI writer prompt - ENHANCED with HTML output and configurable options
GENERAL_ARTICLE_PROMPT = """Je bent een professionele Nederlandse contentschrijver. Je schrijft natuurlijke, menselijke teksten die NIET detecteerbaar zijn als AI-gegenereerd.

OPDRACHT:
Schrijf een artikel over: {onderwerp}

KRITIEK - WOORDENAANTAL (ZEER BELANGRIJK):
✅ Het artikel moet MINIMAAL {min_word_count} woorden bevatten (target: {target_word_count})
✅ Tel de woorden terwijl je schrijft
✅ Maak secties lang genoeg om het woordenaantal te halen
✅ Voeg voldoende diepgang en details toe
✅ Geen intro/outro teksten - alleen het artikel zelf
✅ Als je twijfelt, schrijf MEER in plaats van minder
✅ Elke sectie moet uitgebreid zijn met concrete voorbeelden en uitleg

{sectioning_instruction}

FORMATTING - ZEER BELANGRIJK:
✅ Gebruik ECHTE HTML tags: <h1>, <h2>, <h3>, <p>, <ul>, <li>, <table>, <strong>
✅ NIET markdown (##, ###) - alleen HTML
✅ GEEN code block markers (```html, ```, etc.) - schrijf direct HTML
✅ Headings in Sentence case (alleen eerste letter hoofdletter)
✅ Wrap alle paragrafen in <p> tags
✅ Maximum 1 lege regel tussen elementen

{extra_elements}

{research_context}

SCHRIJFSTIJL:
✅ Gebruik ALTIJD "je" en "jij" (NOOIT "u")
✅ Korte, pakkende zinnen
✅ Afwisselende zinslengte
✅ Directe aanspreking
✅ Natuurlijk en menselijk
✅ Professioneel maar toegankelijk
✅ Concrete voorbeelden en details
✅ Uitgebreide uitleg per sectie

⚠️ VERBODEN WOORDEN EN ZINNEN - ZEER STRENG:
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

NIET doen:
❌ NOOIT "u" gebruiken - ALTIJD "je" en "jij"
❌ NOOIT verboden woorden/zinnen gebruiken
❌ Geen AI-clichés
❌ Geen perfecte, gepolijste zinnen
❌ Geen marketing-taal
❌ GEEN markdown (##, ###) - alleen HTML tags
❌ GEEN code block markers (```html, ```) - direct HTML schrijven

TOON:
- Professioneel maar niet stijf
- Praktisch en direct
- Alsof een expert advies geeft
- Geen verkoop-pitch, maar eerlijk advies
- Licht conversationeel zonder te casual te zijn

{extra_context}

Schrijf nu het artikel van MINIMAAL {min_word_count} woorden (target: {target_word_count}).
ONTHOUD: 
- Gebruik ECHTE HTML tags en GEEN markdown!
- GEEN code block markers - schrijf direct HTML!
- Maak het artikel LANG GENOEG met voldoende details!"""

# WordPress sitemap functions
def fetch_wordpress_sitemap(site_url):
    """Fetch and parse WordPress sitemap to extract internal links"""
    try:
        if not site_url.startswith('http'):
            site_url = 'https://' + site_url
        
        parsed_url = urlparse(site_url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        sitemap_urls = [
            urljoin(base_url, '/sitemap.xml'),
            urljoin(base_url, '/sitemap_index.xml'),
            urljoin(base_url, '/wp-sitemap.xml'),
            urljoin(base_url, '/sitemap-index.xml')
        ]
        
        internal_links = []
        
        for sitemap_url in sitemap_urls:
            try:
                print(f"🔍 Trying sitemap: {sitemap_url}")
                response = requests.get(sitemap_url, timeout=10, headers={
                    'User-Agent': 'Mozilla/5.0 (compatible; WritgoAI/1.0)'
                })
                
                if response.status_code != 200:
                    continue
                
                root = ET.fromstring(response.content)
                
                if 'sitemapindex' in root.tag:
                    print(f"📑 Found sitemap index, parsing sub-sitemaps...")
                    for sitemap in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc'):
                        sub_sitemap_url = sitemap.text
                        try:
                            sub_response = requests.get(sub_sitemap_url, timeout=10, headers={
                                'User-Agent': 'Mozilla/5.0 (compatible; WritgoAI/1.0)'
                            })
                            if sub_response.status_code == 200:
                                sub_root = ET.fromstring(sub_response.content)
                                links = parse_sitemap_urls(sub_root, base_url)
                                internal_links.extend(links)
                        except Exception as e:
                            print(f"⚠️  Error parsing sub-sitemap {sub_sitemap_url}: {e}")
                            continue
                else:
                    links = parse_sitemap_urls(root, base_url)
                    internal_links.extend(links)
                
                if internal_links:
                    print(f"✅ Found {len(internal_links)} internal links from sitemap")
                    return internal_links[:50]
                    
            except Exception as e:
                print(f"⚠️  Error fetching {sitemap_url}: {e}")
                continue
        
        if not internal_links:
            print("⚠️  No sitemap found or no links extracted")
        
        return internal_links
        
    except Exception as e:
        print(f"❌ Error fetching WordPress sitemap: {e}")
        return []

def parse_sitemap_urls(root, base_url):
    """Parse URLs from sitemap XML"""
    links = []
    
    for url_elem in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
        loc = url_elem.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
        
        if loc is not None and loc.text:
            url = loc.text
            
            if url.startswith(base_url):
                path = urlparse(url).path
                title = path.strip('/').split('/')[-1].replace('-', ' ').title()
                
                links.append({
                    'url': url,
                    'title': title
                })
    
    return links

def add_internal_links_to_article(article, internal_links, num_links=3):
    """Add internal links to article content"""
    if not internal_links or num_links <= 0:
        return article
    
    import random
    selected_links = random.sample(internal_links, min(num_links, len(internal_links)))
    
    paragraphs = re.findall(r'<p>.*?</p>', article, re.DOTALL)
    
    if len(paragraphs) < num_links:
        return article
    
    for i, link in enumerate(selected_links):
        position = int((i + 1) * len(paragraphs) / (num_links + 1))
        
        if position < len(paragraphs):
            link_html = f'<p><em>Lees ook: <a href="{link["url"]}" target="_blank">{link["title"]}</a></em></p>'
            paragraph = paragraphs[position]
            article = article.replace(paragraph, paragraph + '\n' + link_html, 1)
    
    return article

# Perplexity AI research
def perplexity_research(topic, num_results=5):
    """Use Perplexity AI to research a topic"""
    if not PERPLEXITY_API_KEY:
        print("⚠️  Perplexity API key not configured")
        return None
    
    try:
        print(f"🔍 Starting Perplexity research for: {topic}")
        
        research_prompt = f"""Onderzoek het volgende onderwerp grondig en geef een gedetailleerde analyse:

Onderwerp: {topic}

Geef de volgende informatie:
1. Een korte samenvatting van de belangrijkste informatie over dit onderwerp
2. De top {num_results} belangrijkste punten die behandeld moeten worden in een artikel
3. Actuele trends en ontwikkelingen
4. Praktische tips en adviezen

Schrijf in het Nederlands en wees specifiek en gedetailleerd."""

        response = requests.post(
            'https://api.perplexity.ai/chat/completions',
            headers={
                'Authorization': f'Bearer {PERPLEXITY_API_KEY}',
                'Content-Type': 'application/json'
            },
            json={
                'model': 'sonar-pro',
                'messages': [
                    {
                        'role': 'system',
                        'content': 'Je bent een onderzoeksassistent die actuele informatie verzamelt en analyseert. Geef altijd bronnen aan.'
                    },
                    {
                        'role': 'user',
                        'content': research_prompt
                    }
                ],
                'temperature': 0.2,
                'max_tokens': 2000,
                'return_citations': True,
                'search_recency_filter': 'month'
            },
            timeout=60
        )
        
        if response.status_code != 200:
            print(f"❌ Perplexity API error: {response.status_code} - {response.text}")
            return None
        
        data = response.json()
        research_content = data['choices'][0]['message']['content']
        citations = []
        if 'citations' in data:
            citations = data['citations']
        
        print(f"✅ Perplexity research completed with {len(citations)} sources")
        
        return {
            'summary': research_content,
            'citations': citations,
            'success': True
        }
        
    except Exception as e:
        print(f"❌ Perplexity research error: {e}")
        return None

# Content generation functions
def generate_topic(anchor1, anchor2, extra="", model="gpt-4o", max_retries=3):
    """Generate article topic based on anchor texts"""
    extra_context = ""
    if extra:
        extra_context = f"\nEXTRA CONTEXT:\n{extra}"
    
    prompt = TOPIC_GENERATION_PROMPT.format(
        anchor1=anchor1,
        anchor2=anchor2,
        extra_context=extra_context
    )
    
    system_prompt = "Je bent een SEO expert. Genereer ALLEEN het onderwerp, geen extra tekst."
    
    for attempt in range(max_retries):
        try:
            if not client:
                raise Exception("OpenAI API key not configured")
            
            response = call_openai_with_correct_params(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=100
            )
            
            topic = response.choices[0].message.content.strip()
            topic = topic.strip('"').strip("'").strip()
            
            print(f"✅ Topic generated: {topic}")
            return topic
            
        except Exception as e:
            print(f"OpenAI Error (attempt {attempt + 1}): {e}")
            if attempt == max_retries - 1:
                raise

def generate_article(onderwerp, anchor1, url1, anchor2, url2, extra="", model="gpt-4o", max_retries=3):
    """Generate linkbuilding article with two anchor texts"""
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
    
    system_prompt = "Je bent een expert Nederlandse contentschrijver. Schrijf natuurlijk en gevarieerd. BELANGRIJK: Gebruik ECHTE HTML tags (<h1>, <h2>, <h3>) en Sentence case voor headings. GEEN markdown code blocks!"
    
    for attempt in range(max_retries):
        try:
            if not client:
                raise Exception("OpenAI API key not configured")
            
            response = call_openai_with_correct_params(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.9,
                max_tokens=2000
            )
            article = response.choices[0].message.content.strip()
            
            # FIXED: Strip markdown code blocks
            article = clean_markdown_blocks(article)
            
            # Check for forbidden words
            has_forbidden, found_phrases = check_forbidden_words(article)
            
            if has_forbidden:
                print(f"⚠️ Attempt {attempt + 1}: Found forbidden phrases: {found_phrases}")
                if attempt < max_retries - 1:
                    prompt += f"\n\n⚠️ KRITIEK: Je gebruikte verboden woorden: {', '.join(found_phrases)}. Herschrijf ZONDER deze woorden!"
                    continue
                else:
                    print("⚠️ Max retries reached. Manually removing forbidden words...")
                    article = re.sub(r'dat is best een opluchting,?\s*toch\??', 'dat is fijn om te weten', article, flags=re.IGNORECASE)
            
            # Convert any remaining markdown to HTML
            article = convert_markdown_to_html(article)
            
            # Add anchor links
            article = add_anchor_links(article, anchor1, url1, anchor2, url2)
            
            # FIXED: Stricter whitespace cleaning
            article = normalize_whitespace(article)
            
            print(f"✅ Article generated successfully (attempt {attempt + 1})")
            return article
            
        except Exception as e:
            print(f"OpenAI Error (attempt {attempt + 1}): {e}")
            if attempt == max_retries - 1:
                raise

def convert_markdown_to_html(text):
    """Convert markdown headings to HTML tags"""
    # Convert H1 (# )
    text = re.sub(r'^#\s+(.+?)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
    # Convert H2 (## )
    text = re.sub(r'^##\s+(.+?)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
    # Convert H3 (### )
    text = re.sub(r'^###\s+(.+?)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    # Convert H4 (#### )
    text = re.sub(r'^####\s+(.+?)$', r'<h4>\1</h4>', text, flags=re.MULTILINE)
    
    return text

def add_anchor_links(article, anchor1, url1, anchor2, url2):
    """Add anchor links to article"""
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
    
    return article

def wrap_paragraphs_in_p_tags(text):
    """Wrap plain text paragraphs in <p> tags"""
    lines = text.split('\n')
    formatted_lines = []
    
    for line in lines:
        line = line.strip()
        
        if not line:
            formatted_lines.append('')
            continue
        
        # Skip if already HTML
        if line.startswith('<'):
            formatted_lines.append(line)
            continue
        
        # Wrap in <p> tag
        formatted_lines.append(f'<p>{line}</p>')
    
    return '\n'.join(formatted_lines)

def calculate_image_frequency(word_count):
    """Calculate number of images based on 1 image per 500 words"""
    return max(1, round(word_count / 500))

def generate_better_pixabay_keywords(topic, section_context=""):
    """
    Generate better Pixabay search keywords
    
    Args:
        topic: Main article topic
        section_context: Context of where the image will be placed
    
    Returns:
        Optimized search query in English
    """
    # Combine topic and context
    full_context = f"{topic} {section_context}".strip()
    
    # Translate to English
    try:
        translator = GoogleTranslator(source='auto', target='en')
        english_query = translator.translate(full_context)
    except:
        english_query = full_context
    
    # Remove common stop words and clean up
    stop_words = ['de', 'het', 'een', 'voor', 'van', 'in', 'op', 'met', 'aan', 'the', 'a', 'an', 'for', 'of', 'in', 'on', 'with', 'to']
    words = english_query.lower().split()
    keywords = [w for w in words if w not in stop_words and len(w) > 2]
    
    # Take first 3-4 most relevant keywords
    optimized_query = ' '.join(keywords[:4])
    
    print(f"🔍 Pixabay search: '{full_context}' → '{optimized_query}'")
    
    return optimized_query

def generate_general_article(onderwerp, word_count=500, extra="", model="gpt-4o", 
                            elements=None, use_research=False, wordpress_site_url=None,
                            sitemap_url=None, max_retries=5):
    """
    Generate general article with optional extra elements
    
    Args:
        onderwerp: Article topic
        word_count: Target word count
        extra: Extra context
        model: Model to use (only gpt-4o supported)
        elements: Dict with optional elements (include_lists, include_tables, include_faq, include_conclusion, pixabay_images, dalle_images, youtube_video)
        use_research: Whether to use Perplexity research
        wordpress_site_url: WordPress site URL for internal links
        sitemap_url: Direct sitemap URL (overrides wordpress_site_url)
        max_retries: Max retry attempts (increased to 5 for word count enforcement)
    """
    if elements is None:
        elements = {}
    
    # Perplexity research
    research_context = ""
    if use_research and PERPLEXITY_API_KEY:
        print("🔍 Performing Perplexity research...")
        research_result = perplexity_research(onderwerp)
        
        if research_result and research_result.get('success'):
            research_context = f"""
ONDERZOEKSRESULTATEN (gebruik deze informatie in je artikel):
{research_result['summary']}

Bronnen: {len(research_result.get('citations', []))} actuele bronnen geraadpleegd
"""
            print("✅ Research completed and added to context")
    
    # FIXED: Calculate minimum word count (90% of target)
    min_word_count = int(word_count * 0.90)
    
    # FIXED: Add sectioning instruction for longer articles
    sectioning_instruction = ""
    if word_count >= 1000:
        num_sections = max(4, word_count // 300)
        sectioning_instruction = f"""
SECTIE STRUCTUUR VOOR LANG ARTIKEL:
✅ Verdeel het artikel in minimaal {num_sections} hoofdsecties (<h2>)
✅ Elke sectie moet minimaal 200-300 woorden bevatten
✅ Voeg subsecties toe (<h3>) waar relevant
✅ Zorg dat elke sectie voldoende diepgang heeft
"""
    
    # Calculate number of images based on word count
    num_images = calculate_image_frequency(word_count)
    
    # Build extra elements instruction
    extra_elements_parts = []
    
    # FIXED: Mandatory list instruction
    if elements.get('include_lists'):
        extra_elements_parts.append("""
LIJSTEN VERPLICHT (ZEER BELANGRIJK):
✅ Je MOET minimaal 1-2 relevante lijsten toevoegen in het artikel
✅ Gebruik HTML list format: <ul><li>item</li></ul>
✅ Lijsten moeten logisch passen in de context
✅ Gebruik voor opsommingen, stappen, tips, voordelen, etc.
✅ VERPLICHT: Artikel wordt afgekeurd als er geen lijst in zit!""")
    
    # FIXED: Mandatory table instruction
    if elements.get('include_tables'):
        extra_elements_parts.append("""
TABEL VERPLICHT (ZEER BELANGRIJK):
✅ Je MOET 1 relevante tabel toevoegen in het artikel
✅ Gebruik HTML table format: <table><tr><th>Header</th></tr><tr><td>Data</td></tr></table>
✅ Minimaal 3 rijen en 2 kolommen
✅ Geef de tabel een duidelijke context in de tekst
✅ Plaats de tabel op een logische plek in het artikel
✅ VERPLICHT: Artikel wordt afgekeurd als er geen tabel in zit!""")
    
    # FIXED: Mandatory FAQ instruction
    if elements.get('include_faq'):
        extra_elements_parts.append("""
FAQ SECTIE VERPLICHT (ZEER BELANGRIJK):
✅ Je MOET een FAQ sectie toevoegen met minimaal 5 vragen
✅ Gebruik <h2>Veelgestelde vragen</h2>
✅ Elke vraag als <h3>[vraag]</h3>
✅ Geef kort en bondig antwoord onder elke vraag in <p> tags
✅ Vragen moeten relevant zijn voor het onderwerp
✅ VERPLICHT: Artikel wordt afgekeurd als er geen FAQ sectie in zit!""")
    
    if elements.get('include_conclusion', True):  # Default to True
        extra_elements_parts.append("""
CONCLUSIE VEREIST:
✅ Voeg een conclusie sectie toe met <h2>Conclusie</h2>
✅ Vat de belangrijkste punten samen
✅ Geef een afsluitende gedachte of call-to-action""")
    
    # Image placeholders based on word count
    if elements.get('pixabay_images', 0) > 0 or num_images > 0:
        actual_num_images = elements.get('pixabay_images', num_images)
        extra_elements_parts.append(f"""
AFBEELDING PLACEHOLDERS VEREIST:
✅ Voeg EXACT {actual_num_images} afbeelding placeholder(s) toe (1 per 500 woorden)
✅ Gebruik format: [IMAGE: beschrijving in het Engels]
✅ Bijvoorbeeld: [IMAGE: yoga mat exercises morning routine]
✅ Plaats gelijkmatig verdeeld door het artikel
✅ Beschrijvingen moeten SPECIFIEK en in ENGELS zijn
✅ Denk aan: wat zou een goede stockfoto zijn voor deze sectie?""")
    
    if elements.get('dalle_images', 0) > 0:
        num_dalle = elements.get('dalle_images')
        style = elements.get('dalle_style', 'realistic photo')
        extra_elements_parts.append(f"""
AI AFBEELDING PLACEHOLDERS VEREIST:
✅ Voeg {num_dalle} AI afbeelding placeholder(s) toe
✅ Gebruik format: [AI-IMAGE: gedetailleerde beschrijving in het Engels]
✅ Stijl: {style}
✅ Bijvoorbeeld: [AI-IMAGE: modern minimalist yoga studio with natural lighting, {style}]
✅ Beschrijvingen moeten ZEER GEDETAILLEERD zijn voor AI generatie
✅ Plaats op logische plekken in het artikel""")
    
    if elements.get('youtube_video'):
        extra_elements_parts.append("""
YOUTUBE VIDEO PLACEHOLDER VEREIST:
✅ Voeg 1 YouTube video placeholder toe
✅ Gebruik format: [YOUTUBE: zoekterm in het Engels]
✅ Bijvoorbeeld: [YOUTUBE: best yoga exercises for beginners]
✅ Plaats op een logische plek (vaak na intro of voor conclusie)
✅ Zoekterm moet specifiek en relevant zijn""")
    
    extra_elements_instruction = "\n".join(extra_elements_parts) if extra_elements_parts else ""
    
    extra_context = ""
    if extra:
        extra_context = f"\nEXTRA CONTEXT:\n{extra}"
    
    prompt = GENERAL_ARTICLE_PROMPT.format(
        onderwerp=onderwerp,
        min_word_count=min_word_count,
        target_word_count=word_count,
        sectioning_instruction=sectioning_instruction,
        extra_elements=extra_elements_instruction,
        research_context=research_context,
        extra_context=extra_context
    )
    
    system_prompt = "Je bent een expert Nederlandse contentschrijver. Schrijf natuurlijk en gevarieerd. BELANGRIJK: Gebruik ECHTE HTML tags (<h1>, <h2>, <h3>, <p>) en Sentence case voor headings. GEEN markdown code blocks! Schrijf LANG GENOEG om het woordenaantal te halen!"
    
    model = "gpt-4o"
    
    for attempt in range(max_retries):
        try:
            if not client:
                raise Exception("OpenAI API key not configured")
            
            # FIXED: Increase max_tokens for longer articles
            max_tokens = min(4000, max(2000, word_count * 2))
            
            response = call_openai_with_correct_params(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.9,
                max_tokens=max_tokens
            )
            article = response.choices[0].message.content.strip()
            
            # FIXED: Strip markdown code blocks FIRST
            article = clean_markdown_blocks(article)
            
            # Check for forbidden words
            has_forbidden, found_phrases = check_forbidden_words(article)
            
            if has_forbidden:
                print(f"⚠️ Attempt {attempt + 1}: Found forbidden phrases: {found_phrases}")
                if attempt < max_retries - 1:
                    prompt += f"\n\n⚠️ KRITIEK: Je gebruikte verboden woorden: {', '.join(found_phrases)}. Herschrijf ZONDER deze woorden!"
                    continue
                else:
                    print("⚠️ Max retries reached. Manually removing forbidden words...")
                    article = re.sub(r'dat is best een opluchting,?\s*toch\??', 'dat is fijn om te weten', article, flags=re.IGNORECASE)
            
            # FIXED: Validate word count
            is_valid_count, actual_count, count_message = enforce_word_count(article, word_count)
            print(count_message)
            
            if not is_valid_count and attempt < max_retries - 1:
                print(f"⚠️ Retrying due to insufficient word count...")
                prompt += f"\n\n⚠️ KRITIEK: Je artikel had slechts {actual_count} woorden, maar moet minimaal {min_word_count} woorden hebben (target: {word_count}). Schrijf een LANGER artikel met meer details en uitleg per sectie!"
                continue
            
            # FIXED: Validate mandatory options
            is_valid_options, missing = enforce_options(article, elements)
            
            if not is_valid_options and attempt < max_retries - 1:
                print(f"⚠️ Missing required elements: {', '.join(missing)}")
                prompt += f"\n\n⚠️ KRITIEK: Je vergat de volgende VERPLICHTE elementen: {', '.join(missing)}. Voeg deze toe aan het artikel!"
                continue
            
            # Convert any remaining markdown to HTML
            article = convert_markdown_to_html(article)
            
            # Process placeholders
            article = process_article_placeholders(article, onderwerp, elements)
            
            # Wrap paragraphs in <p> tags if not already
            article = wrap_paragraphs_in_p_tags(article)
            
            # FIXED: Stricter whitespace cleaning
            article = normalize_whitespace(article)
            
            # Add WordPress internal links if sitemap URL provided
            if sitemap_url:
                print(f"🔗 Fetching internal links from sitemap: {sitemap_url}")
                internal_links = fetch_sitemap_urls(sitemap_url)
                if internal_links:
                    article = add_internal_links_to_article(article, internal_links, num_links=3)
                    print(f"✅ Added {min(3, len(internal_links))} internal links to article")
            elif wordpress_site_url:
                print(f"🔗 Fetching internal links from {wordpress_site_url}")
                internal_links = fetch_wordpress_sitemap(wordpress_site_url)
                if internal_links:
                    article = add_internal_links_to_article(article, internal_links, num_links=3)
                    print(f"✅ Added {min(3, len(internal_links))} internal links to article")
            
            # Final validation summary
            final_count = count_words(article)
            print(f"✅ Article generated successfully with {model} (attempt {attempt + 1})")
            print(f"📊 Final word count: {final_count}/{word_count} ({final_count/word_count*100:.1f}%)")
            
            return article
            
        except Exception as e:
            print(f"API Error with {model} (attempt {attempt + 1}): {e}")
            if attempt == max_retries - 1:
                raise

def process_article_placeholders(article, onderwerp, elements):
    """Process placeholders in article and replace with actual content"""
    if not elements:
        return article
    
    # Process Pixabay image placeholders
    if elements.get('pixabay_images', 0) > 0:
        image_pattern = r'\[IMAGE:\s*([^\]]+)\]'
        matches = re.findall(image_pattern, article)
        
        for match in matches:
            search_query = match.strip()
            # Generate better keywords
            optimized_query = generate_better_pixabay_keywords(onderwerp, search_query)
            
            try:
                images = search_pixabay_images(optimized_query, per_page=3)
                if images:
                    img_url = images[0]['url']
                    img_tag = f'<img src="{img_url}" alt="{search_query}" style="max-width: 100%; height: auto; margin: 20px 0; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">'
                    article = article.replace(f'[IMAGE: {match}]', img_tag, 1)
                    print(f"✅ Pixabay image added for: {optimized_query}")
                else:
                    article = article.replace(f'[IMAGE: {match}]', '', 1)
                    print(f"⚠️  No Pixabay image found for: {optimized_query}")
            except Exception as e:
                print(f"❌ Error fetching Pixabay image for '{search_query}': {e}")
                article = article.replace(f'[IMAGE: {match}]', '', 1)
    
    # Process DALL-E image placeholders
    if elements.get('dalle_images', 0) > 0:
        ai_image_pattern = r'\[AI-IMAGE:\s*([^\]]+)\]'
        matches = re.findall(ai_image_pattern, article)
        
        for match in matches:
            prompt = match.strip()
            try:
                result = generate_dalle_image(prompt)
                if result.get('success') and result.get('image_url'):
                    img_url = result['image_url']
                    img_tag = f'<img src="{img_url}" alt="AI Generated: {prompt[:50]}" style="max-width: 100%; height: auto; margin: 20px 0; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">'
                    article = article.replace(f'[AI-IMAGE: {match}]', img_tag, 1)
                    print(f"✅ DALL-E image generated for: {prompt[:50]}")
                else:
                    error_msg = result.get('error', 'Unknown error')
                    print(f"❌ DALL-E image generation failed: {error_msg}")
                    article = article.replace(f'[AI-IMAGE: {match}]', '', 1)
            except Exception as e:
                print(f"❌ Error generating DALL-E image for '{prompt}': {e}")
                article = article.replace(f'[AI-IMAGE: {match}]', '', 1)
    
    # Process YouTube video placeholders
    if elements.get('youtube_video'):
        youtube_pattern = r'\[YOUTUBE:\s*([^\]]+)\]'
        matches = re.findall(youtube_pattern, article)
        
        for match in matches:
            search_term = match.strip()
            search_url = f"https://www.youtube.com/results?search_query={search_term.replace(' ', '+')}"
            youtube_embed = f'<div style="margin: 20px 0; padding: 15px; background: #f0f0f0; border-radius: 8px;"><p><strong>📺 Aanbevolen video:</strong> <a href="{search_url}" target="_blank">Bekijk videos over "{search_term}"</a></p></div>'
            article = article.replace(f'[YOUTUBE: {match}]', youtube_embed, 1)
    
    return article

def translate_to_english(text):
    """Translate search query to English for maximum Pixabay results"""
    if not text or not text.strip():
        return text
    
    try:
        translator = GoogleTranslator(source='auto', target='en')
        translated = translator.translate(text.strip())
        print(f"🌐 Translated '{text}' → '{translated}'")
        return translated
    except Exception as e:
        print(f"⚠️  Translation failed for '{text}': {e}. Using original query.")
        return text

def search_pixabay_images(query, per_page=10, image_type='photo', orientation='horizontal'):
    """Search for images on Pixabay"""
    if not PIXABAY_API_KEY:
        raise Exception("Pixabay API key not configured")
    
    # Translate query to English
    query = translate_to_english(query)
    
    per_page = max(3, min(per_page, 200))
    
    try:
        url = "https://pixabay.com/api/"
        params = {
            'key': PIXABAY_API_KEY,
            'q': query,
            'per_page': per_page,
            'lang': 'en'  # Force English for better results
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code != 200:
            print(f"Pixabay API Error: {response.status_code} - {response.text}")
            return []
        
        try:
            data = response.json()
        except json.JSONDecodeError as e:
            print(f"❌ Pixabay JSON parsing error: {e}")
            return []
        
        if data.get('totalHits', 0) == 0:
            return []
        
        images = []
        for hit in data.get('hits', []):
            images.append({
                'id': hit.get('id'),
                'preview': hit.get('previewURL'),
                'url': hit.get('largeImageURL'),
                'width': hit.get('imageWidth'),
                'height': hit.get('imageHeight'),
                'tags': hit.get('tags'),
                'user': hit.get('user')
            })
        
        return images
        
    except requests.exceptions.Timeout:
        print("Pixabay API Timeout")
        return []
    except requests.exceptions.RequestException as e:
        print(f"Pixabay API Request Error: {e}")
        return []
    except Exception as e:
        print(f"Pixabay API Exception: {e}")
        return []

def generate_dalle_image(prompt):
    """Generate image using DALL-E 3"""
    if not client:
        return {"success": False, "error": "OpenAI API key not configured"}
    
    try:
        print(f"🎨 Generating DALL-E image: {prompt[:50]}...")
        
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )
        
        if response.data and len(response.data) > 0:
            image_url = response.data[0].url
            print(f"✅ DALL-E image generated successfully")
            return {
                "success": True,
                "image_url": image_url
            }
        else:
            print(f"❌ DALL-E response has no data")
            return {
                "success": False,
                "error": "No image data in response"
            }
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ DALL-E generation error: {error_msg}")
        return {
            "success": False,
            "error": error_msg
        }

# API ENDPOINTS
@app.route('/')
def index():
    """Serve the main HTML page"""
    return send_file('templates/index.html')

@app.route('/api/generate-topic', methods=['POST'])
def api_generate_topic():
    """Generate article topic"""
    try:
        print("📝 Starting topic generation...")
        data = request.json
        anchor1 = data.get('anchor1', '').strip()
        anchor2 = data.get('anchor2', '').strip()
        extra = data.get('extra', '').strip()
        model = data.get('model', 'gpt-4o')
        
        if not anchor1 or not anchor2:
            return jsonify({"success": False, "error": "Both anchor texts are required"}), 400
        
        topic = generate_topic(anchor1, anchor2, extra, model)
        print(f"✅ Topic generated successfully")
        return jsonify({"success": True, "topic": topic})
        
    except Exception as e:
        import traceback
        print(f"❌ Error in topic generation: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/generate-article', methods=['POST'])
def api_generate_article():
    """Generate linkbuilding article"""
    try:
        print("📝 Starting linkbuilding article generation...")
        data = request.json
        onderwerp = data.get('onderwerp', '').strip()
        anchor1 = data.get('anchor1', '').strip()
        url1 = data.get('url1', '').strip()
        anchor2 = data.get('anchor2', '').strip()
        url2 = data.get('url2', '').strip()
        extra = data.get('extra', '').strip()
        model = data.get('model', 'gpt-4o')
        
        if not all([onderwerp, anchor1, url1, anchor2, url2]):
            return jsonify({"success": False, "error": "All fields are required"}), 400
        
        article = generate_article(onderwerp, anchor1, url1, anchor2, url2, extra, model)
        
        text_content = re.sub(r'<[^>]+>', '', article)
        word_count = len(text_content.split())
        
        print(f"✅ Linkbuilding article generated successfully ({word_count} words)")
        return jsonify({
            "success": True,
            "article": article,
            "word_count": word_count
        })
        
    except Exception as e:
        import traceback
        print(f"❌ Error in article generation: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/generate-general-article', methods=['POST'])
def api_generate_general_article():
    """Generate general article with optional elements"""
    try:
        print("📝 Starting general article generation...")
        data = request.json
        onderwerp = data.get('onderwerp', '').strip()
        word_count = data.get('word_count', 800)
        extra = data.get('extra', '').strip()
        model = data.get('model', 'gpt-4o')
        
        # Optional elements
        elements = {
            'include_lists': data.get('include_lists', False),
            'include_tables': data.get('include_tables', False),
            'include_faq': data.get('include_faq', False),
            'include_conclusion': data.get('include_conclusion', True),
            'pixabay_images': data.get('pixabay_images', 0),
            'dalle_images': data.get('dalle_images', 0),
            'dalle_style': data.get('dalle_style', 'realistic photo'),
            'youtube_video': data.get('youtube_video', False)
        }
        
        use_research = data.get('perplexity_research', False)
        wordpress_site_url = data.get('wordpress_site_url', '').strip()
        sitemap_url = data.get('sitemap_url', '').strip()
        
        if not onderwerp:
            return jsonify({"success": False, "error": "Onderwerp is required"}), 400
        
        article = generate_general_article(
            onderwerp=onderwerp,
            word_count=word_count,
            extra=extra,
            model=model,
            elements=elements,
            use_research=use_research,
            wordpress_site_url=wordpress_site_url,
            sitemap_url=sitemap_url
        )
        
        text_content = re.sub(r'<[^>]+>', '', article)
        actual_word_count = len(text_content.split())
        
        print(f"✅ General article generated successfully ({actual_word_count} words)")
        return jsonify({
            "success": True,
            "article": article,
            "word_count": actual_word_count
        })
        
    except Exception as e:
        import traceback
        print(f"❌ Error in general article generation: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
