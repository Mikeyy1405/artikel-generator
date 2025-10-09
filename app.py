
#!/usr/bin/env python3
"""
WritgoAI Content Generator v19
Multi-feature content creation platform with WordPress integration
Enhanced with extra elements: tables, FAQ, bold text, Pixabay images, DALL-E images, YouTube videos
NEW: Perplexity research, WordPress sitemap integration, improved word count accuracy

RECENT FIXES (v19):
- Removed overly restrictive "voordelen" forbidden phrases check
- Increased Perplexity API timeout from 30s to 60s
- Increased Gunicorn worker timeout from 300s to 600s
- Added comprehensive error handling with JSON responses (no more HTML errors)
- Added detailed logging for all API endpoints
- Added global exception handler to ensure JSON responses
- Improved error messages with traceback details
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

# Error handler for JSON parsing errors
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

# Ensure all responses have correct Content-Type
@app.after_request
def after_request(response):
    """Ensure JSON responses have correct Content-Type"""
    if response.status_code >= 200 and response.status_code < 300:
        if not response.content_type or 'text/html' in response.content_type:
            # Only set JSON content type for API endpoints
            if request.path.startswith('/api/'):
                response.content_type = 'application/json'
    return response

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
    
    # WordPress sites table with new fields
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
    
    # Knowledge base documents per site
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
    
    # Add new columns to existing wordpress_sites table if they don't exist
    try:
        cursor.execute('ALTER TABLE wordpress_sites ADD COLUMN sitemap_url TEXT')
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    try:
        cursor.execute('ALTER TABLE wordpress_sites ADD COLUMN context TEXT')
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    conn.commit()
    conn.close()
    print("✅ Database initialized")

# Initialize database on startup
init_db()

# Load API keys from environment variables or secrets file
def load_api_keys():
    """Load API keys from environment variables (Render) or abacusai_auth_secrets.json (local)"""
    keys = {
        'openai': None,
        'anthropic': None,
        'originality': None,
        'pixabay': None,
        'perplexity': None
    }
    
    # First, try to load from environment variables (for Render deployment)
    keys['openai'] = os.getenv('OPENAI_API_KEY')
    keys['anthropic'] = os.getenv('ANTHROPIC_API_KEY')
    keys['originality'] = os.getenv('ORIGINALITY_API_KEY')
    keys['pixabay'] = os.getenv('PIXABAY_API_KEY')
    keys['perplexity'] = os.getenv('PERPLEXITY_API_KEY')
    
    # If not found in env vars, try loading from secrets file (for local development)
    secrets_path = '/home/ubuntu/.config/abacusai_auth_secrets.json'
    if os.path.exists(secrets_path):
        try:
            with open(secrets_path, 'r') as f:
                secrets = json.load(f)
            
            # OpenAI
            if not keys['openai'] and 'openai' in secrets and 'secrets' in secrets['openai']:
                if 'api_key' in secrets['openai']['secrets']:
                    keys['openai'] = secrets['openai']['secrets']['api_key']['value']
            
            # Anthropic
            if not keys['anthropic'] and 'anthropic' in secrets and 'secrets' in secrets['anthropic']:
                if 'api_key' in secrets['anthropic']['secrets']:
                    keys['anthropic'] = secrets['anthropic']['secrets']['api_key']['value']
            
            # Originality.AI
            if not keys['originality'] and 'originality.ai' in secrets and 'secrets' in secrets['originality.ai']:
                if 'api_key' in secrets['originality.ai']['secrets']:
                    keys['originality'] = secrets['originality.ai']['secrets']['api_key']['value']
            
            # Pixabay
            if not keys['pixabay'] and 'pixabay' in secrets and 'secrets' in secrets['pixabay']:
                if 'api_key' in secrets['pixabay']['secrets']:
                    keys['pixabay'] = secrets['pixabay']['secrets']['api_key']['value']
            
            # Perplexity
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

# Initialize OpenAI client with increased timeout for DALL-E
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
        print("⚠️  Anthropic library not installed. Run: pip install anthropic")
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

# FORBIDDEN PHRASES - Relaxed list (removed "voordelen" as it's too restrictive)
FORBIDDEN_PHRASES = [
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

def to_sentence_case(text):
    """
    Convert text to sentence case (first letter uppercase, rest lowercase)
    Preserves proper nouns and acronyms if they're already capitalized
    """
    if not text:
        return text
    
    # First letter uppercase, rest as-is (to preserve proper nouns)
    return text[0].upper() + text[1:]

def call_openai_with_correct_params(model, messages, temperature=0.9, max_tokens=2000):
    """Call OpenAI API with correct parameters based on model"""
    # GPT-5 and newer models use max_completion_tokens instead of max_tokens
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

HEADINGS - ZEER BELANGRIJK (SENTENCE CASE):
✅ H1: Gebruik EXACT het onderwerp "{onderwerp}" (met "H1: " ervoor)
✅ H2 en H3: Gebruik Sentence case - alleen eerste letter hoofdletter
✅ Voorbeeld GOED: "H2: Dit is een heading" (niet "H2: Dit Is Een Heading")
✅ H2 en H3: Maak deze RELEVANT voor het specifieke onderwerp
✅ H2 en H3: GEEN vaste templates of standaard koppen
✅ H2 en H3: Pas aan bij de inhoud en het onderwerp
✅ Markeer alle headings met "H1: ", "H2: ", "H3: " ervoor
✅ Laatste H2 moet zijn: "H2: Conclusie" (met hoofdletter C)

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
- Aangepast aan het onderwerp (formeel bij formele onderwerpen, toegankelijk bij toegankelijke onderwerpen)

TECHNISCHE EISEN:
- Woordenaantal: EXACT 500 woorden (±2 woorden toegestaan)
- Anchor teksten: Beide verplicht, PRECIES 1 KEER elk, SUBTIEL verweven
- H1: EXACT het onderwerp "{onderwerp}"
- Headings: Sentence case (alleen eerste letter hoofdletter), relevant voor het onderwerp, GEEN vaste templates, WEL met "H1: ", "H2: ", "H3: " prefix
- Conclusie: ALTIJD "H2: Conclusie" met hoofdletter C
- Alinea's: 2-4 zinnen per alinea
- Geen intro zoals "In dit artikel..." - begin direct met de kern

{extra_context}

Schrijf nu het artikel. Begin direct met de H1 titel: "H1: {onderwerp}".
ONTHOUD: Headings in Sentence case (alleen eerste letter hoofdletter)!"""

# General AI writer prompt - ENHANCED with extra elements and word count enforcement
GENERAL_ARTICLE_PROMPT = """Je bent een professionele Nederlandse contentschrijver. Je schrijft natuurlijke, menselijke teksten die NIET detecteerbaar zijn als AI-gegenereerd.

OPDRACHT:
Schrijf een artikel over: {onderwerp}

{word_count_instruction}

KRITIEK - WOORDENAANTAL:
✅ Het artikel moet EXACT {target_word_count} woorden bevatten
✅ Tel de woorden terwijl je schrijft
✅ Pas de lengte van secties aan om het exacte aantal te bereiken
✅ Geen intro/outro teksten - alleen het artikel zelf
✅ Elke sectie moet voldoende diepgang hebben om het woordenaantal te halen

{extra_elements}

{research_context}

SCHRIJFSTIJL:
✅ Gebruik ALTIJD "je" en "jij" (NOOIT "u")
✅ Korte, pakkende zinnen
✅ Afwisselende zinslengte
✅ Directe aanspreking
✅ Natuurlijk en menselijk
✅ Professioneel maar toegankelijk
✅ Concrete voorbeelden

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

TOON:
- Professioneel maar niet stijf
- Praktisch en direct
- Alsof een expert advies geeft
- Geen verkoop-pitch, maar eerlijk advies
- Licht conversationeel zonder te casual te zijn

{extra_context}

Schrijf nu het artikel van EXACT {target_word_count} woorden.
ONTHOUD: ABSOLUUT GEEN "voordelen" of "voordeel" gebruiken!"""

# ============================================================================
# WORDPRESS SITEMAP INTEGRATION
# ============================================================================

def fetch_wordpress_sitemap(site_url):
    """
    Fetch and parse WordPress sitemap to extract internal links
    
    Args:
        site_url: WordPress site URL (e.g., https://example.com)
    
    Returns:
        List of internal links with titles
    """
    try:
        # Normalize URL
        if not site_url.startswith('http'):
            site_url = 'https://' + site_url
        
        parsed_url = urlparse(site_url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        # Try common sitemap locations
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
                
                # Parse XML
                root = ET.fromstring(response.content)
                
                # Handle sitemap index (contains links to other sitemaps)
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
                    # Regular sitemap
                    links = parse_sitemap_urls(root, base_url)
                    internal_links.extend(links)
                
                if internal_links:
                    print(f"✅ Found {len(internal_links)} internal links from sitemap")
                    return internal_links[:50]  # Limit to 50 links
                    
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
    
    # Find all URL entries
    for url_elem in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
        loc = url_elem.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
        
        if loc is not None and loc.text:
            url = loc.text
            
            # Only include URLs from the same domain
            if url.startswith(base_url):
                # Extract title from URL (last part of path)
                path = urlparse(url).path
                title = path.strip('/').split('/')[-1].replace('-', ' ').title()
                
                links.append({
                    'url': url,
                    'title': title
                })
    
    return links

def add_internal_links_to_article(article, internal_links, num_links=3):
    """
    Add internal links to article content
    
    Args:
        article: HTML article content
        internal_links: List of internal link dicts with 'url' and 'title'
        num_links: Number of internal links to add
    
    Returns:
        Article with internal links added
    """
    if not internal_links or num_links <= 0:
        return article
    
    # Select random links
    import random
    selected_links = random.sample(internal_links, min(num_links, len(internal_links)))
    
    # Find good places to insert links (after paragraphs)
    paragraphs = re.findall(r'<p>.*?</p>', article, re.DOTALL)
    
    if len(paragraphs) < num_links:
        return article
    
    # Insert links at strategic positions
    for i, link in enumerate(selected_links):
        # Calculate position (spread evenly throughout article)
        position = int((i + 1) * len(paragraphs) / (num_links + 1))
        
        if position < len(paragraphs):
            # Create link HTML
            link_html = f'<p><em>Lees ook: <a href="{link["url"]}" target="_blank">{link["title"]}</a></em></p>'
            
            # Insert after the paragraph at position
            paragraph = paragraphs[position]
            article = article.replace(paragraph, paragraph + '\n' + link_html, 1)
    
    return article

# ============================================================================
# PERPLEXITY AI RESEARCH
# ============================================================================

def perplexity_research(topic, num_results=5):
    """
    Use Perplexity AI to research a topic and gather key information
    
    Args:
        topic: Topic to research
        num_results: Number of key points to extract
    
    Returns:
        Dict with research summary, sources, and key points
    """
    if not PERPLEXITY_API_KEY:
        print("⚠️  Perplexity API key not configured")
        return None
    
    try:
        print(f"🔍 Starting Perplexity research for: {topic}")
        
        # Research prompt
        research_prompt = f"""Onderzoek het volgende onderwerp grondig en geef een gedetailleerde analyse:

Onderwerp: {topic}

Geef de volgende informatie:
1. Een korte samenvatting van de belangrijkste informatie over dit onderwerp
2. De top {num_results} belangrijkste punten die behandeld moeten worden in een artikel
3. Actuele trends en ontwikkelingen
4. Praktische tips en adviezen

Schrijf in het Nederlands en wees specifiek en gedetailleerd."""

        # Call Perplexity API
        response = requests.post(
            'https://api.perplexity.ai/chat/completions',
            headers={
                'Authorization': f'Bearer {PERPLEXITY_API_KEY}',
                'Content-Type': 'application/json'
            },
            json={
                'model': 'llama-3.1-sonar-large-128k-online',
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
            timeout=60  # Increased from 30 to 60 seconds
        )
        
        if response.status_code != 200:
            print(f"❌ Perplexity API error: {response.status_code} - {response.text}")
            return None
        
        data = response.json()
        
        # Extract research content
        research_content = data['choices'][0]['message']['content']
        
        # Extract citations if available
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

# ============================================================================
# CONTENT GENERATION FUNCTIONS
# ============================================================================

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
    
    system_prompt = "Je bent een expert Nederlandse contentschrijver. Schrijf natuurlijk en gevarieerd. BELANGRIJK: Headings in Sentence case (alleen eerste letter hoofdletter)."
    
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
                    article = re.sub(r'dat is best een opluchting,?\s*toch\??', 'dat is fijn om te weten', article, flags=re.IGNORECASE)
            
            article = re.sub(r'^H2:\s*conclusie\s*$', 'H2: Conclusie', article, flags=re.MULTILINE | re.IGNORECASE)
            article = format_article_html(article, anchor1, url1, anchor2, url2)
            
            print(f"✅ Article generated successfully (attempt {attempt + 1})")
            return article
            
        except Exception as e:
            print(f"OpenAI Error (attempt {attempt + 1}): {e}")
            if attempt == max_retries - 1:
                raise

def enforce_word_count(article, target_word_count, onderwerp, model="gpt-4o"):
    """
    Enforce exact word count by extending or trimming article
    
    Args:
        article: Current article content (HTML)
        target_word_count: Target word count
        onderwerp: Article topic
        model: AI model to use
    
    Returns:
        Article with correct word count
    """
    # Strip HTML and count words
    text_content = re.sub(r'<[^>]+>', '', article)
    current_word_count = len(text_content.split())
    
    difference = target_word_count - current_word_count
    
    # If within 5% tolerance, accept it
    tolerance = int(target_word_count * 0.05)
    if abs(difference) <= tolerance:
        print(f"✅ Word count {current_word_count} is within tolerance of {target_word_count}")
        return article
    
    print(f"⚠️  Word count adjustment needed: {current_word_count} → {target_word_count} (difference: {difference})")
    
    try:
        if difference > 0:
            # Need to add more content
            prompt = f"""Het volgende artikel over "{onderwerp}" heeft {current_word_count} woorden, maar moet {target_word_count} woorden hebben.

Voeg {difference} woorden toe door bestaande secties uit te breiden met meer details, voorbeelden en diepgang.

BELANGRIJK:
- Behoud de bestaande structuur en headings
- Voeg GEEN nieuwe secties toe
- Breid bestaande alinea's uit met relevante informatie
- Blijf on-topic en relevant
- Behoud de HTML formatting

Huidig artikel:
{article}

Geef het uitgebreide artikel terug met EXACT {target_word_count} woorden."""
        else:
            # Need to remove content
            prompt = f"""Het volgende artikel over "{onderwerp}" heeft {current_word_count} woorden, maar moet {target_word_count} woorden hebben.

Verwijder {abs(difference)} woorden door minder belangrijke details te schrappen, maar behoud de kernboodschap.

BELANGRIJK:
- Behoud de bestaande structuur en headings
- Verwijder GEEN hele secties
- Maak alinea's korter en bondiger
- Blijf on-topic en relevant
- Behoud de HTML formatting

Huidig artikel:
{article}

Geef het ingekorte artikel terug met EXACT {target_word_count} woorden."""
        
        if not client:
            print("⚠️  Cannot adjust word count - OpenAI client not available")
            return article
        
        response = call_openai_with_correct_params(
            model=model,
            messages=[
                {"role": "system", "content": "Je bent een expert editor die artikelen precies op het juiste woordenaantal brengt."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=4000
        )
        
        adjusted_article = response.choices[0].message.content.strip()
        
        # Verify new word count
        new_text_content = re.sub(r'<[^>]+>', '', adjusted_article)
        new_word_count = len(new_text_content.split())
        
        print(f"✅ Word count adjusted: {current_word_count} → {new_word_count} (target: {target_word_count})")
        
        return adjusted_article
        
    except Exception as e:
        print(f"❌ Error adjusting word count: {e}")
        return article

def generate_general_article(onderwerp, word_count=500, extra="", model="gpt-4o", 
                            elements=None, use_research=False, wordpress_site_url=None,
                            max_retries=3):
    """
    Generate general article with optional extra elements
    
    Args:
        onderwerp: Article topic
        word_count: Target word count
        extra: Extra context
        model: Model to use (only gpt-4o supported)
        elements: Dict with optional elements
        use_research: Whether to use Perplexity research
        wordpress_site_url: WordPress site URL for internal links
        max_retries: Max retry attempts
    """
    # Default elements
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
    
    word_count_instruction = f"Schrijf een artikel van EXACT {word_count} woorden. Tel de woorden en zorg dat je precies op dit aantal uitkomt."
    
    # Build extra elements instruction
    extra_elements_parts = []
    
    if elements.get('include_table'):
        extra_elements_parts.append("""
TABEL VEREIST:
✅ Voeg 1 relevante tabel toe in het artikel
✅ Gebruik HTML table format: <table>, <tr>, <th>, <td>
✅ Minimaal 3 rijen en 2 kolommen
✅ Geef de tabel een duidelijke context in de tekst
✅ Plaats de tabel op een logische plek in het artikel""")
    
    if elements.get('include_faq'):
        extra_elements_parts.append("""
FAQ SECTIE VEREIST:
✅ Voeg een FAQ sectie toe met minimaal 5 vragen
✅ Gebruik H2: Veelgestelde vragen
✅ Elke vraag als H3: [vraag]
✅ Geef kort en bondig antwoord onder elke vraag
✅ Vragen moeten relevant zijn voor het onderwerp""")
    
    if elements.get('include_bold'):
        extra_elements_parts.append("""
BOLD TEXT VEREIST:
✅ Gebruik <strong> tags voor belangrijke woorden/zinnen
✅ Minimaal 5-10 belangrijke termen bold maken
✅ Gebruik dit voor nadruk op kernpunten
✅ Niet overdrijven - alleen echt belangrijke zaken""")
    
    if elements.get('pixabay_images', 0) > 0:
        num_images = elements.get('pixabay_images')
        extra_elements_parts.append(f"""
AFBEELDING PLACEHOLDERS VEREIST:
✅ Voeg {num_images} afbeelding placeholder(s) toe in het artikel
✅ Gebruik format: [IMAGE: beschrijving in het Engels]
✅ Bijvoorbeeld: [IMAGE: yoga mat exercises morning routine]
✅ Plaats op logische plekken in het artikel
✅ Beschrijvingen moeten SPECIFIEK en in ENGELS zijn
✅ Denk aan: wat zou een goede stockfoto zijn voor deze sectie?""")
    
    if elements.get('dalle_images', 0) > 0:
        num_images = elements.get('dalle_images')
        style = elements.get('dalle_style', 'realistic photo')
        extra_elements_parts.append(f"""
AI AFBEELDING PLACEHOLDERS VEREIST:
✅ Voeg {num_images} AI afbeelding placeholder(s) toe
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
        word_count_instruction=word_count_instruction,
        target_word_count=word_count,
        extra_elements=extra_elements_instruction,
        research_context=research_context,
        extra_context=extra_context
    )
    
    system_prompt = "Je bent een expert Nederlandse contentschrijver. Schrijf natuurlijk en gevarieerd. BELANGRIJK: Headings in Sentence case (alleen eerste letter hoofdletter)."
    
    # Only use GPT-4o
    model = "gpt-4o"
    
    for attempt in range(max_retries):
        try:
            # Use OpenAI API with gpt-4o only
            if not client:
                raise Exception("OpenAI API key not configured")
            
            response = call_openai_with_correct_params(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.9,
                max_tokens=4000
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
                    article = re.sub(r'dat is best een opluchting,?\s*toch\??', 'dat is fijn om te weten', article, flags=re.IGNORECASE)
            
            article = re.sub(r'^H2:\s*conclusie\s*$', 'H2: Conclusie', article, flags=re.MULTILINE | re.IGNORECASE)
            
            # Process placeholders BEFORE formatting HTML
            article = process_article_placeholders(article, onderwerp, elements)
            article = format_article_html(article)
            
            # Enforce word count
            article = enforce_word_count(article, word_count, onderwerp, model)
            
            # Add WordPress internal links if site URL provided
            if wordpress_site_url:
                print(f"🔗 Fetching internal links from {wordpress_site_url}")
                internal_links = fetch_wordpress_sitemap(wordpress_site_url)
                if internal_links:
                    article = add_internal_links_to_article(article, internal_links, num_links=3)
                    print(f"✅ Added {min(3, len(internal_links))} internal links to article")
            
            print(f"✅ Article generated successfully with {model} (attempt {attempt + 1})")
            return article
            
        except Exception as e:
            print(f"API Error with {model} (attempt {attempt + 1}): {e}")
            if attempt == max_retries - 1:
                raise

def format_article_html(article, anchor1=None, url1=None, anchor2=None, url2=None):
    """Convert article with H1/H2/H3 markers to HTML with improved list and table formatting"""
    
    # Replace heading markers with HTML tags (Sentence case preserved)
    # Use word boundaries to ensure we only match heading markers at the start of lines
    article = re.sub(r'^H1:\s*(.+?)$', r'<h1>\1</h1>', article, flags=re.MULTILINE)
    article = re.sub(r'^H2:\s*(.+?)$', r'<h2>\1</h2>', article, flags=re.MULTILINE)
    article = re.sub(r'^H3:\s*(.+?)$', r'<h3>\1</h3>', article, flags=re.MULTILINE)
    
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
    
    # Split into lines for processing
    lines = article.split('\n')
    formatted_lines = []
    in_list = False
    in_table = False
    
    for line in lines:
        line = line.strip()
        
        if not line:
            if in_list:
                formatted_lines.append('</ul>')
                in_list = False
            formatted_lines.append('')
            continue
        
        # Check if line is already HTML (heading, table, etc.)
        if line.startswith('<'):
            if in_list and not line.startswith('<li>'):
                formatted_lines.append('</ul>')
                in_list = False
            formatted_lines.append(line)
            
            # Track table state
            if '<table' in line.lower():
                in_table = True
            elif '</table>' in line.lower():
                in_table = False
            continue
        
        # Skip processing if we're inside a table
        if in_table:
            formatted_lines.append(line)
            continue
        
        # Check for list items (lines starting with -, *, or numbers)
        if re.match(r'^[-*•]\s+', line) or re.match(r'^\d+\.\s+', line):
            if not in_list:
                formatted_lines.append('<ul>')
                in_list = True
            
            # Remove list marker and wrap in <li>
            item_text = re.sub(r'^[-*•]\s+', '', line)
            item_text = re.sub(r'^\d+\.\s+', '', item_text)
            formatted_lines.append(f'<li>{item_text}</li>')
        else:
            # Regular paragraph
            if in_list:
                formatted_lines.append('</ul>')
                in_list = False
            
            # Don't wrap if already wrapped in HTML tags
            if not re.match(r'^<[^>]+>.*</[^>]+>$', line):
                formatted_lines.append(f'<p>{line}</p>')
            else:
                formatted_lines.append(line)
    
    # Close any open list
    if in_list:
        formatted_lines.append('</ul>')
    
    return '\n'.join(formatted_lines)

def refine_article(article, topic, anchors, user_request, model="gpt-4o", max_retries=3):
    """Refine article based on user request"""
    
    # Extract text content for context
    text_content = re.sub(r'<[^>]+>', '', article)
    
    # Build refinement prompt
    prompt = f"""Je bent een expert content editor. Je hebt een artikel geschreven over "{topic}" en de gebruiker wil aanpassingen.

HUIDIG ARTIKEL (tekst):
{text_content[:2000]}...

GEBRUIKER VRAAGT:
{user_request}

BELANGRIJKE REGELS:
✅ Behoud de HTML structuur en formatting
✅ Behoud bestaande anchor links: {anchors}
✅ Headings in Sentence case (alleen eerste letter hoofdletter)
✅ Gebruik "je" en "jij" (NOOIT "u")

Geef het VOLLEDIGE aangepaste artikel terug in HTML formaat."""

    system_prompt = "Je bent een expert Nederlandse content editor. Schrijf natuurlijk en gevarieerd."
    
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
                max_tokens=4000
            )
            
            refined_article = response.choices[0].message.content.strip()
            
            # Check for forbidden words
            has_forbidden, found_phrases = check_forbidden_words(refined_article)
            
            if has_forbidden:
                print(f"⚠️ Attempt {attempt + 1}: Found forbidden phrases in refinement: {found_phrases}")
                if attempt < max_retries - 1:
                    prompt += f"\n\n⚠️ KRITIEK: Je gebruikte verboden woorden: {', '.join(found_phrases)}. Herschrijf ZONDER deze woorden!"
                    continue
                else:
                    # Manually remove forbidden words
                    pass
            print(f"✅ Article refined successfully (attempt {attempt + 1})")
            return refined_article
            
        except Exception as e:
            print(f"OpenAI Refinement Error (attempt {attempt + 1}): {e}")
            if attempt == max_retries - 1:
                raise

def process_article_placeholders(article, onderwerp, elements):
    """
    Process placeholders in article and replace with actual content
    
    Placeholders:
    - [IMAGE: description] -> Fetch from Pixabay
    - [AI-IMAGE: description] -> Generate with DALL-E
    - [YOUTUBE: search term] -> Embed YouTube video
    """
    if not elements:
        return article
    
    # Process Pixabay image placeholders
    if elements.get('pixabay_images', 0) > 0:
        image_pattern = r'\[IMAGE:\s*([^\]]+)\]'
        matches = re.findall(image_pattern, article)
        
        for match in matches:
            search_query = match.strip()
            try:
                images = search_pixabay_images(search_query, per_page=3)
                if images:
                    img_url = images[0]['url']
                    img_tag = f'<img src="{img_url}" alt="{search_query}" style="max-width: 100%; height: auto; margin: 20px 0; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">'
                    article = article.replace(f'[IMAGE: {match}]', img_tag, 1)
                else:
                    # Remove placeholder if no image found
                    article = article.replace(f'[IMAGE: {match}]', '', 1)
            except Exception as e:
                print(f"Error fetching Pixabay image for '{search_query}': {e}")
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
            # Create YouTube search embed (opens search results)
            search_url = f"https://www.youtube.com/results?search_query={search_term.replace(' ', '+')}"
            youtube_embed = f'<div style="margin: 20px 0; padding: 15px; background: #f0f0f0; border-radius: 8px;"><p><strong>📺 Aanbevolen video:</strong> <a href="{search_url}" target="_blank">Bekijk videos over "{search_term}"</a></p></div>'
            article = article.replace(f'[YOUTUBE: {match}]', youtube_embed, 1)
    
    return article

def translate_to_english(text):
    """
    Translate search query to English for maximum Pixabay results
    
    Args:
        text: Search query in any language
    
    Returns:
        Translated text in English (or original if already English or translation fails)
    """
    if not text or not text.strip():
        return text
    
    try:
        # Detect if text is already in English (simple check)
        # If translation fails or text is already English, return original
        translator = GoogleTranslator(source='auto', target='en')
        translated = translator.translate(text.strip())
        
        # Return translated text
        print(f"🌐 Translated '{text}' → '{translated}'")
        return translated
    except Exception as e:
        # If translation fails, return original query
        print(f"⚠️  Translation failed for '{text}': {e}. Using original query.")
        return text

def search_pixabay_images(query, per_page=10, image_type='photo', orientation='horizontal'):
    """
    Search for images on Pixabay
    
    Args:
        query: Search term (will be automatically translated to English)
        per_page: Number of results (default 10, max 200, min 3)
        image_type: 'all', 'photo', 'illustration', 'vector'
        orientation: 'all', 'horizontal', 'vertical'
    
    Returns:
        List of image objects with URLs and metadata
    """
    if not PIXABAY_API_KEY:
        raise Exception("Pixabay API key not configured")
    
    # Translate query to English for maximum results
    query = translate_to_english(query)
    
    # Ensure per_page is within valid range (3-200)
    per_page = max(3, min(per_page, 200))
    
    try:
        url = "https://pixabay.com/api/"
        params = {
            'key': PIXABAY_API_KEY,
            'q': query,
            'per_page': per_page
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code != 200:
            print(f"Pixabay API Error: {response.status_code} - {response.text}")
            return []
        
        # Check if response is valid JSON
        try:
            data = response.json()
        except json.JSONDecodeError as e:
            print(f"❌ Pixabay JSON parsing error: {e}")
            print(f"Response content: {response.text[:200]}")
            return []
        
        if data.get('totalHits', 0) == 0:
            return []
        
        # Format results
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

def search_pixabay_videos(query, per_page=10):
    """Search for videos on Pixabay"""
    if not PIXABAY_API_KEY:
        return {"error": "Pixabay API key not configured"}
    
    # Translate query to English
    query = translate_to_english(query)
    
    try:
        url = "https://pixabay.com/api/videos/"
        params = {
            'key': PIXABAY_API_KEY,
            'q': query,
            'per_page': min(per_page, 200)
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code != 200:
            return {"error": f"API Error: {response.status_code}"}
        
        # Check if response is valid JSON
        try:
            data = response.json()
        except json.JSONDecodeError as e:
            print(f"❌ Pixabay Videos JSON parsing error: {e}")
            return {"error": "Invalid JSON response"}
        
        if data.get('totalHits', 0) == 0:
            return {"videos": [], "total": 0}
        
        # Format results
        videos = []
        for hit in data.get('hits', []):
            videos.append({
                'id': hit.get('id'),
                'preview': hit.get('picture_id'),
                'url': hit.get('videos', {}).get('large', {}).get('url'),
                'width': hit.get('videos', {}).get('large', {}).get('width'),
                'height': hit.get('videos', {}).get('large', {}).get('height'),
                'tags': hit.get('tags'),
                'user': hit.get('user')
            })
        
        return {
            "videos": videos,
            "total": data.get('totalHits', 0)
        }
        
    except requests.exceptions.Timeout:
        return {"error": "Request timeout"}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
    except Exception as e:
        print(f"Pixabay Video API Exception: {e}")
        return {"error": str(e)}

def generate_dalle_image(prompt):
    """
    Generate image using DALL-E 3
    
    Args:
        prompt: Image description prompt
    
    Returns:
        Dict with success status and image_url or error
    """
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
        
        # Extract image URL from response
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

# ============================================================================
# API ENDPOINTS
# ============================================================================

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
        
        # Count words
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
        print(f"❌ Error in linkbuilding article generation: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/generate-general-article', methods=['POST'])
def api_generate_general_article():
    """Generate general article with optional extra elements"""
    try:
        print("📝 Starting general article generation...")
        data = request.json
        onderwerp = data.get('onderwerp', '').strip()
        word_count = int(data.get('word_count', 500))
        extra = data.get('extra', '').strip()
        model = data.get('model', 'gpt-4o')
        use_research = data.get('use_research', False)
        wordpress_site_url = data.get('wordpress_site_url', '').strip()
        
        # Extract extra elements
        elements = {
            'include_table': data.get('include_table', False),
            'include_faq': data.get('include_faq', False),
            'include_bold': data.get('include_bold', False),
            'pixabay_images': int(data.get('pixabay_images', 0)),
            'dalle_images': int(data.get('dalle_images', 0)),
            'dalle_style': data.get('dalle_style', 'realistic photo'),
            'youtube_video': data.get('youtube_video', False)
        }
        
        if not onderwerp:
            return jsonify({"success": False, "error": "Topic is required"}), 400
        
        print(f"📊 Target word count: {word_count}, Research: {use_research}")
        article = generate_general_article(
            onderwerp, 
            word_count, 
            extra, 
            model, 
            elements,
            use_research=use_research,
            wordpress_site_url=wordpress_site_url if wordpress_site_url else None
        )
        
        # Count words
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

@app.route('/api/refine-article', methods=['POST'])
def api_refine_article():
    """Refine article based on user request"""
    try:
        print("✏️ Starting article refinement...")
        data = request.json
        article = data.get('article', '').strip()
        topic = data.get('topic', '').strip()
        user_request = data.get('request', '').strip()
        anchors = data.get('anchors', {})
        model = data.get('model', 'gpt-4o')
        
        if not all([article, user_request]):
            return jsonify({"success": False, "error": "Article and request are required"}), 400
        
        refined_article = refine_article(article, topic, anchors, user_request, model=model)
        
        # Count words
        text_content = re.sub(r'<[^>]+>', '', refined_article)
        word_count = len(text_content.split())
        
        print(f"✅ Article refined successfully ({word_count} words)")
        return jsonify({
            "success": True,
            "article": refined_article,
            "word_count": word_count
        })
        
    except Exception as e:
        import traceback
        print(f"❌ Error in article refinement: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/search-pixabay-images', methods=['POST'])
def api_search_pixabay_images():
    """Search Pixabay for images"""
    try:
        data = request.json
        query = data.get('query', '').strip()
        per_page = int(data.get('per_page', 10))
        
        if not query:
            return jsonify({"error": "Query is required"}), 400
        
        images = search_pixabay_images(
            query=query,
            per_page=per_page
        )
        
        return jsonify({
            "success": True,
            "images": images,
            "total": len(images)
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/search-pixabay-videos', methods=['POST'])
def api_search_pixabay_videos():
    """Search Pixabay for videos"""
    try:
        data = request.json
        query = data.get('query', '').strip()
        per_page = int(data.get('per_page', 10))
        
        if not query:
            return jsonify({"error": "Query is required"}), 400
        
        result = search_pixabay_videos(query=query, per_page=per_page)
        
        if "error" in result:
            return jsonify(result), 500
        
        return jsonify({
            "success": True,
            "videos": result.get("videos", []),
            "total": result.get("total", 0)
        })
        
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
        
        if result.get('success'):
            return jsonify(result)
        else:
            return jsonify(result), 500
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/fetch-wordpress-sitemap', methods=['POST'])
def api_fetch_wordpress_sitemap():
    """Fetch WordPress sitemap and extract internal links"""
    try:
        data = request.json
        site_url = data.get('site_url', '').strip()
        
        if not site_url:
            return jsonify({"error": "Site URL is required"}), 400
        
        internal_links = fetch_wordpress_sitemap(site_url)
        
        return jsonify({
            "success": True,
            "links": internal_links,
            "total": len(internal_links)
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/perplexity-research', methods=['POST'])
def api_perplexity_research():
    """Perform Perplexity AI research on a topic"""
    try:
        data = request.json
        topic = data.get('topic', '').strip()
        
        if not topic:
            return jsonify({"error": "Topic is required"}), 400
        
        result = perplexity_research(topic)
        
        if result and result.get('success'):
            return jsonify(result)
        else:
            return jsonify({"error": "Research failed"}), 500
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============================================================================
# WORDPRESS SITES API ENDPOINTS
# ============================================================================

@app.route('/api/wordpress-sites', methods=['GET'])
def api_get_wordpress_sites():
    """Get all WordPress sites"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, site_name, site_url, username, created_at FROM wordpress_sites ORDER BY site_name')
        sites = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify({
            "success": True,
            "sites": sites
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/wordpress-sites', methods=['POST'])
def api_add_wordpress_site():
    """Add a new WordPress site with automatic sitemap detection and link extraction"""
    try:
        data = request.json
        site_name = data.get('site_name', '').strip()
        site_url = data.get('site_url', '').strip()
        username = data.get('username', '').strip()
        app_password = data.get('app_password', '').strip()
        context = data.get('context', '').strip()
        
        if not all([site_name, site_url, username, app_password]):
            return jsonify({"error": "All fields are required"}), 400
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if site already exists
        cursor.execute('SELECT id FROM wordpress_sites WHERE site_name = ?', (site_name,))
        if cursor.fetchone():
            conn.close()
            return jsonify({"error": "Site with this name already exists"}), 400
        
        # Automatically detect sitemap
        sitemap_result = find_sitemap(site_url)
        sitemap_url = sitemap_result.get('sitemap_url', '') if sitemap_result.get('success') else ''
        
        # Insert new site
        cursor.execute('''
            INSERT INTO wordpress_sites (site_name, site_url, username, app_password, sitemap_url, context)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (site_name, site_url, username, app_password, sitemap_url, context))
        
        site_id = cursor.lastrowid
        
        # Extract internal links from homepage
        internal_links_result = extract_internal_links(site_url, max_links=50)
        if internal_links_result.get('success'):
            for link in internal_links_result.get('links', []):
                cursor.execute('''
                    INSERT INTO internal_links (site_id, anchor_text, url)
                    VALUES (?, ?, ?)
                ''', (site_id, link['anchor_text'], link['url']))
        
        # Detect affiliate links from homepage
        try:
            response = requests.get(site_url, timeout=15, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            if response.status_code == 200:
                affiliate_result = detect_affiliate_links(response.text)
                if affiliate_result.get('success'):
                    for link in affiliate_result.get('links', []):
                        cursor.execute('''
                            INSERT INTO affiliate_links (site_id, anchor_text, url)
                            VALUES (?, ?, ?)
                        ''', (site_id, link['anchor_text'], link['url']))
        except:
            pass  # Continue even if affiliate detection fails
        
        conn.commit()
        conn.close()
        
        return jsonify({
            "success": True,
            "site_id": site_id,
            "sitemap_url": sitemap_url,
            "internal_links_count": internal_links_result.get('count', 0) if internal_links_result.get('success') else 0,
            "message": "WordPress site added successfully with automatic link extraction"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/wordpress-sites/<int:site_id>', methods=['DELETE'])
def api_delete_wordpress_site(site_id):
    """Delete a WordPress site"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM wordpress_sites WHERE id = ?', (site_id,))
        
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({"error": "Site not found"}), 404
        
        conn.commit()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "WordPress site deleted successfully"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============================================================================
# INTERNAL LINKS & AFFILIATE LINKS API ENDPOINTS
# ============================================================================

@app.route('/api/wordpress-sites/<int:site_id>/internal-links', methods=['GET'])
def api_get_internal_links(site_id):
    """Get internal links for a WordPress site"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, anchor_text, url, created_at 
            FROM internal_links 
            WHERE site_id = ?
            ORDER BY created_at DESC
        ''', (site_id,))
        links = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify({
            "success": True,
            "links": links
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/wordpress-sites/<int:site_id>/affiliate-links', methods=['GET'])
def api_get_affiliate_links(site_id):
    """Get affiliate links for a WordPress site"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, anchor_text, url, created_at 
            FROM affiliate_links 
            WHERE site_id = ?
            ORDER BY created_at DESC
        ''', (site_id,))
        links = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify({
            "success": True,
            "links": links
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============================================================================
# KNOWLEDGE BASE API ENDPOINTS
# ============================================================================

@app.route('/api/wordpress-sites/<int:site_id>/knowledge-base', methods=['POST'])
def api_upload_knowledge_base(site_id):
    """Upload a document to the knowledge base for a WordPress site"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Read file content
        content = file.read().decode('utf-8', errors='ignore')
        filename = file.filename
        file_type = filename.split('.')[-1] if '.' in filename else 'txt'
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if site exists
        cursor.execute('SELECT id FROM wordpress_sites WHERE id = ?', (site_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({"error": "Site not found"}), 404
        
        # Insert document
        cursor.execute('''
            INSERT INTO knowledge_base (site_id, filename, content, file_type)
            VALUES (?, ?, ?, ?)
        ''', (site_id, filename, content, file_type))
        
        doc_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            "success": True,
            "doc_id": doc_id,
            "message": "Document uploaded successfully"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/wordpress-sites/<int:site_id>/knowledge-base', methods=['GET'])
def api_get_knowledge_base(site_id):
    """Get all knowledge base documents for a WordPress site"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, filename, file_type, created_at 
            FROM knowledge_base 
            WHERE site_id = ?
            ORDER BY created_at DESC
        ''', (site_id,))
        documents = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify({
            "success": True,
            "documents": documents
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/wordpress-sites/<int:site_id>/knowledge-base/<int:doc_id>', methods=['DELETE'])
def api_delete_knowledge_base(site_id, doc_id):
    """Delete a knowledge base document"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM knowledge_base WHERE id = ? AND site_id = ?', (doc_id, site_id))
        
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({"error": "Document not found"}), 404
        
        conn.commit()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Document deleted successfully"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============================================================================
# ARTICLES API ENDPOINTS
# ============================================================================

@app.route('/api/articles', methods=['GET'])
def api_get_articles():
    """Get all articles"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, title, article_type, word_count, human_score, ai_score, created_at 
            FROM articles 
            ORDER BY created_at DESC
        ''')
        articles = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify({
            "success": True,
            "articles": articles
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
