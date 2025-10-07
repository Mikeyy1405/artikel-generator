#!/usr/bin/env python3
"""
WritgoAI Content Generator v14
Multi-feature content creation platform with WordPress integration
Enhanced with extra elements: tables, FAQ, bold text, Pixabay images, DALL-E images, YouTube videos
NEW: Claude AI models support + "Best of All" combination mode
Mobile responsive design with hamburger menu
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
try:
    import anthropic
except ImportError:
    anthropic = None

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
PERPLEXITY_API_KEY = api_keys.get('perplexity')  # Safe get

# Initialize OpenAI client
client = None
if OPENAI_API_KEY:
    http_client = httpx.Client(timeout=60.0, follow_redirects=True)
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

def call_claude_api(prompt, system_prompt, model="claude-sonnet-4", max_tokens=4000):
    """
    Call Claude API with given prompt
    
    Args:
        prompt: User prompt
        system_prompt: System prompt
        model: Claude model to use
        max_tokens: Maximum tokens to generate
    
    Returns:
        Generated text
    """
    if not anthropic_client:
        raise Exception("Anthropic API key not configured or library not installed")
    
    # Map friendly names to actual model IDs
    model_mapping = {
        "claude-sonnet-4": "claude-3-5-sonnet-20241022",  # Latest available
        "claude-opus-4": "claude-3-opus-20240229",  # Latest opus
        "claude-sonnet-3.7": "claude-3-5-sonnet-20241022",
        "claude-sonnet-3.5": "claude-3-5-sonnet-20241022",
        "claude-haiku-3.5": "claude-3-5-haiku-20241022"
    }
    
    actual_model = model_mapping.get(model, model)
    
    try:
        message = anthropic_client.messages.create(
            model=actual_model,
            max_tokens=max_tokens,
            temperature=0.9,
            system=system_prompt,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        return message.content[0].text
    except Exception as e:
        raise Exception(f"Claude API error: {str(e)}")

def perplexity_research(topic, num_results=5):
    """
    Use Perplexity AI to research a topic and gather information from top Google results
    
    Args:
        topic: The topic to research
        num_results: Number of sources to consider (default 5)
    
    Returns:
        dict with 'summary', 'sources', and 'key_points'
    """
    if not PERPLEXITY_API_KEY:
        return {
            'summary': '',
            'sources': [],
            'key_points': [],
            'error': 'Perplexity API key not configured'
        }
    
    try:
        # Perplexity API endpoint
        url = "https://api.perplexity.ai/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Research prompt
        research_prompt = f"""Onderzoek het volgende onderwerp grondig: "{topic}"

Geef me:
1. Een uitgebreide samenvatting van de belangrijkste informatie
2. De top {num_results} belangrijkste punten die ik moet behandelen
3. Actuele trends en ontwikkelingen
4. Wat de beste artikelen over dit onderwerp bespreken
5. Unieke invalshoeken die ik kan gebruiken

Wees specifiek en geef concrete informatie die ik kan gebruiken om een beter artikel te schrijven dan wat er al online staat."""

        payload = {
            "model": "llama-3.1-sonar-large-128k-online",  # Perplexity's online search model
            "messages": [
                {
                    "role": "system",
                    "content": "Je bent een expert content researcher. Zoek actuele, betrouwbare informatie en geef concrete, bruikbare inzichten."
                },
                {
                    "role": "user",
                    "content": research_prompt
                }
            ],
            "temperature": 0.2,
            "top_p": 0.9,
            "return_citations": True,
            "search_recency_filter": "month",  # Focus on recent content
            "stream": False
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract research results
        content = data['choices'][0]['message']['content']
        citations = data.get('citations', [])
        
        # Parse key points from the response
        key_points = []
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                # Remove numbering/bullets
                clean_line = re.sub(r'^[\d\.\-•\*\s]+', '', line).strip()
                if len(clean_line) > 20:  # Only substantial points
                    key_points.append(clean_line)
        
        return {
            'summary': content,
            'sources': citations[:num_results],  # Limit to requested number
            'key_points': key_points[:10],  # Top 10 key points
            'success': True
        }
        
    except requests.exceptions.Timeout:
        return {
            'summary': '',
            'sources': [],
            'key_points': [],
            'error': 'Perplexity API timeout - research took too long'
        }
    except requests.exceptions.RequestException as e:
        return {
            'summary': '',
            'sources': [],
            'key_points': [],
            'error': f'Perplexity API error: {str(e)}'
        }
    except Exception as e:
        return {
            'summary': '',
            'sources': [],
            'key_points': [],
            'error': f'Research error: {str(e)}'
        }

def generate_with_best_of_all(prompt, system_prompt, word_count=500):
    """
    Generate content using "Best of All" approach:
    1. Generate with GPT-4.1 (structure & SEO)
    2. Generate with Claude Sonnet 4 (natural writing)
    3. Generate with Claude Opus 4 (creativity & depth)
    4. Combine the best elements from all three
    
    Args:
        prompt: User prompt
        system_prompt: System prompt
        word_count: Target word count
    
    Returns:
        Combined best article
    """
    results = {}
    
    # 1. GPT-4.1 - Structure & SEO optimization
    try:
        if client:
            response = call_openai_with_correct_params(
                model="gpt-4.1",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=4000
            )
            results['gpt4'] = response.choices[0].message.content.strip()
    except Exception as e:
        print(f"GPT-4.1 failed: {e}")
        results['gpt4'] = None
    
    # 2. Claude Sonnet 4 - Natural, human-like writing
    try:
        if anthropic_client:
            results['claude_sonnet'] = call_claude_api(
                prompt=prompt,
                system_prompt=system_prompt,
                model="claude-sonnet-4",
                max_tokens=4000
            )
    except Exception as e:
        print(f"Claude Sonnet 4 failed: {e}")
        results['claude_sonnet'] = None
    
    # 3. Claude Opus 4 - Creativity & depth
    try:
        if anthropic_client:
            results['claude_opus'] = call_claude_api(
                prompt=prompt,
                system_prompt=system_prompt,
                model="claude-opus-4",
                max_tokens=4000
            )
    except Exception as e:
        print(f"Claude Opus 4 failed: {e}")
        results['claude_opus'] = None
    
    # Filter out None results
    valid_results = {k: v for k, v in results.items() if v is not None}
    
    if not valid_results:
        raise Exception("All models failed to generate content")
    
    # If only one model succeeded, return that
    if len(valid_results) == 1:
        return list(valid_results.values())[0]
    
    # Combine the best elements
    combination_prompt = f"""Je hebt 3 verschillende versies van hetzelfde artikel ontvangen van verschillende AI modellen.
Jouw taak is om het BESTE artikel te maken door de sterke punten van elk te combineren:

VERSION 1 (GPT-4.1 - Structuur & SEO):
{results.get('gpt4', 'Niet beschikbaar')}

VERSION 2 (Claude Sonnet 4 - Natuurlijk schrijven):
{results.get('claude_sonnet', 'Niet beschikbaar')}

VERSION 3 (Claude Opus 4 - Creativiteit & diepgang):
{results.get('claude_opus', 'Niet beschikbaar')}

OPDRACHT:
Maak het ULTIEME artikel door:
✅ De beste structuur te kiezen (waarschijnlijk van GPT-4.1)
✅ De meest natuurlijke schrijfstijl te gebruiken (waarschijnlijk van Claude Sonnet)
✅ De meest creatieve en diepgaande inzichten toe te voegen (waarschijnlijk van Claude Opus)
✅ Alle H1, H2, H3 headers te behouden
✅ Alle anchor links te behouden
✅ Ongeveer {word_count} woorden
✅ GEEN "voordelen" of "voordeel" gebruiken

Geef ALLEEN het gecombineerde artikel terug, geen uitleg."""

    # Use Claude Sonnet 4 for the combination (best at natural writing)
    try:
        if anthropic_client:
            final_article = call_claude_api(
                prompt=combination_prompt,
                system_prompt="Je bent een expert editor die het beste uit meerdere artikelen combineert tot één perfect artikel.",
                model="claude-sonnet-4",
                max_tokens=4000
            )
            return final_article
    except Exception as e:
        print(f"Combination failed: {e}")
        # Fallback: return the longest article
        return max(valid_results.values(), key=len)

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

❌ ABSOLUUT VERBODEN IN HET ONDERWERP:
- "voordelen van"
- "voordeel van"
- "voor- en nadelen"
- Gebruik alternatieven: "wat biedt", "waarom kiezen voor", "alles over", "gids voor"

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

# General AI writer prompt - ENHANCED with extra elements
GENERAL_ARTICLE_PROMPT = """Je bent een professionele Nederlandse contentschrijver. Je schrijft natuurlijke, menselijke teksten die NIET detecteerbaar zijn als AI-gegenereerd.

OPDRACHT:
Schrijf een artikel over: {onderwerp}

{word_count_instruction}

{extra_elements}

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
    
    # Check if "Best of All" mode - use GPT-4.1
    if model == "best-of-all":
        print("🌟 Using Best of All mode - using GPT-4.1 (best model)")
        model = "gpt-4.1"
    
    extra_context = ""
    if extra:
        extra_context = f"\nEXTRA CONTEXT:\n{extra}"
    
    prompt = TOPIC_GENERATION_PROMPT.format(
        anchor1=anchor1,
        anchor2=anchor2,
        extra_context=extra_context
    )
    
    try:
        response = call_openai_with_correct_params(
            model=model,
            messages=[
                {"role": "system", "content": "Je bent een SEO expert die ALGEMENE artikel onderwerpen bedenkt. GEEN productnamen, merknamen, keywords, dubbele punten of jaartallen. ABSOLUUT VERBODEN: 'voordelen van', 'voordeel van'. Gebruik alternatieven zoals 'wat biedt', 'waarom kiezen voor', 'alles over'."},
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
        
        # Check for forbidden phrases in topic
        forbidden_in_topic = ['voordelen van', 'voordeel van', 'voor- en nadelen']
        topic_lower = topic.lower()
        for phrase in forbidden_in_topic:
            if phrase in topic_lower:
                print(f"⚠️ Topic contains forbidden phrase '{phrase}', cleaning...")
                # Replace with alternatives
                topic = re.sub(r'\bvoordelen van\b', 'wat biedt', topic, flags=re.IGNORECASE)
                topic = re.sub(r'\bvoordeel van\b', 'waarom kiezen voor', topic, flags=re.IGNORECASE)
                topic = re.sub(r'\bvoor- en nadelen\b', 'alles over', topic, flags=re.IGNORECASE)
                break
        
        return topic
    except Exception as e:
        print(f"OpenAI Topic Generation Error: {e}")
        raise

def extract_topic_from_urls(anchor1, url1, anchor2, url2, context="", placement_domain=""):
    """Extract topic suggestion from URLs and anchors using AI"""
    if not client:
        return None
    
    try:
        # Build comprehensive context
        full_context = f"""Analyseer deze linkbuilding informatie en suggereer een KORT en SPECIFIEK onderwerp voor een artikel.

ANCHOR 1: {anchor1}
URL 1: {url1}

ANCHOR 2: {anchor2}
URL 2: {url2}"""

        if placement_domain:
            full_context += f"\n\nPLAATSINGS DOMEIN: {placement_domain}"
        
        if context:
            full_context += f"\n\nEXTRA CONTEXT: {context}"

        full_context += """

Geef ALLEEN het onderwerp terug, zonder uitleg. Het onderwerp moet:
- Kort zijn (max 5-7 woorden)
- Relevant zijn voor BEIDE anchors EN urls
- Natuurlijk klinken als artikel titel
- In het Nederlands zijn
- GEEN "voordelen van" of "voordeel van" bevatten
- Gebruik alternatieven zoals "wat biedt", "waarom kiezen voor", "alles over"

Voorbeeld output: "Kleine lease auto voor zakelijk gebruik"
"""
        
        response = call_openai_with_correct_params(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Je bent een SEO expert die perfecte artikel onderwerpen bedenkt. VERBODEN: 'voordelen van', 'voordeel van'. Gebruik alternatieven."},
                {"role": "user", "content": full_context}
            ],
            temperature=0.7,
            max_tokens=50
        )
        
        topic = response.choices[0].message.content.strip()
        # Remove quotes if present
        topic = topic.strip('"').strip("'")
        print(f"✅ Auto-generated topic: {topic}")
        return topic
        
    except Exception as e:
        print(f"⚠️ Topic extraction error: {e}")
        return None

def analyze_placement_domain(domain_url):
    """Analyze placement domain to adjust writing style"""
    if not domain_url:
        return ""
    
    try:
        # Extract domain from URL
        from urllib.parse import urlparse
        parsed = urlparse(domain_url if domain_url.startswith('http') else f'https://{domain_url}')
        domain = parsed.netloc or parsed.path
        
        print(f"📊 Analyzing domain: {domain}")
        
        # Scrape homepage (with timeout)
        try:
            response = requests.get(f'https://{domain}', timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            content = response.text[:5000]  # First 5000 chars
        except:
            print(f"⚠️ Could not scrape {domain}, using domain name only")
            content = domain
        
        # Use AI to analyze
        if client:
            prompt = f"""Analyseer deze website en geef een KORTE stijlgids (max 3 zinnen):

DOMEIN: {domain}
CONTENT SAMPLE: {content[:1000]}

Geef aan:
1. Tone of voice (formeel/informeel/professioneel/casual)
2. Doelgroep (zakelijk/particulier/breed)
3. Schrijfstijl aanbeveling

Hou het KORT en PRAKTISCH."""
            
            response = call_openai_with_correct_params(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Je bent een content strategist."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=150
            )
            
            analysis = response.choices[0].message.content.strip()
            print(f"✅ Domain analysis complete")
            return f"\n\nSTIJLGIDS VOOR {domain}:\n{analysis}"
        
        return ""
        
    except Exception as e:
        print(f"⚠️ Domain analysis error: {e}")
        return ""

def call_openai_with_correct_params(model, messages, temperature=0.9, max_tokens=2000):
    """Call OpenAI API with correct parameters based on model"""

    def uses_max_completion_tokens(model_name: str) -> bool:
        """Return True when the model expects the `max_completion_tokens` parameter."""
        if model_name in ["o1-preview", "o1-mini"]:
            return True
        # GPT-5 modellen ondersteunen geen `max_tokens` parameter meer
        return model_name.startswith("gpt-5")

    if uses_max_completion_tokens(model):
        kwargs = {
            "model": model,
            "messages": messages,
            "max_completion_tokens": max_tokens
        }

        # Alleen o1 modellen negeren temperature volgens OpenAI specificaties
        if not model.startswith("o1"):
            kwargs["temperature"] = temperature

        return client.chat.completions.create(**kwargs)

    # Regular models use max_tokens
    return client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens
    )

def generate_article(onderwerp, anchor1, url1, anchor2, url2, extra="", model="gpt-4o", max_retries=3):
    """Generate linkbuilding article with forbidden words check"""
    if not client:
        raise Exception("OpenAI API key not configured")
    
    # Check if "Best of All" mode - use GPT-4.1 (best available model)
    if model == "best-of-all":
        print("🌟 Using Best of All mode - using GPT-4.1 (best model)")
        model = "gpt-4.1"
    
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
            response = call_openai_with_correct_params(
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

def generate_general_article(onderwerp, word_count=500, extra="", model="gpt-4o", 
                            elements=None, max_retries=3, use_research=False):
    """
    Generate general article with optional extra elements
    Supports GPT models, Claude models, and "Best of All" combination
    
    Args:
        onderwerp: Article topic
        word_count: Target word count
        extra: Extra context
        model: Model to use (gpt-4o, gpt-4.1, gpt-5, claude-sonnet-4, claude-opus-4, etc., or "best-of-all")
        elements: Dict with optional elements:
            - include_table: bool
            - include_faq: bool
            - include_bold: bool
            - pixabay_images: int (number of images)
            - dalle_images: int (number of AI images)
            - dalle_style: str (style for DALL-E images)
            - youtube_video: bool
        max_retries: Max retry attempts
        use_research: If True, use Perplexity to research topic first
    """
    # Default elements
    if elements is None:
        elements = {}
    
    # Perform research if requested
    research_context = ""
    research_sources = []
    if use_research and PERPLEXITY_API_KEY:
        print(f"🔍 Researching topic: {onderwerp}")
        research_result = perplexity_research(onderwerp, num_results=5)
        
        if research_result.get('success'):
            research_context = f"""
RESEARCH RESULTATEN (gebruik deze informatie om een beter artikel te schrijven):

{research_result['summary']}

BELANGRIJKE PUNTEN OM TE BEHANDELEN:
{chr(10).join(f"• {point}" for point in research_result['key_points'])}

BRONNEN (voeg deze toe aan het einde van het artikel):
{chr(10).join(f"• {source}" for source in research_result['sources'])}

Gebruik deze research om:
1. Actuele en accurate informatie te geven
2. Unieke invalshoeken te vinden die andere artikelen niet hebben
3. Diepgaander in te gaan op belangrijke aspecten
4. Betere content te maken dan wat er al online staat
"""
            research_sources = research_result['sources']
            print(f"✅ Research completed: {len(research_result['key_points'])} key points, {len(research_sources)} sources")
        else:
            print(f"⚠️ Research failed: {research_result.get('error', 'Unknown error')}")
    elif use_research and not PERPLEXITY_API_KEY:
        print("⚠️ Research requested but Perplexity API key not configured")
    
    word_count_instruction = f"Schrijf een artikel van ongeveer {word_count} woorden."
    
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
✅ Gebruik H2: Veelgestelde Vragen
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
    
    # Add research context if available
    if research_context:
        extra_context += f"\n\n{research_context}"
    
    prompt = GENERAL_ARTICLE_PROMPT.format(
        onderwerp=onderwerp,
        word_count_instruction=word_count_instruction,
        extra_elements=extra_elements_instruction,
        extra_context=extra_context
    )
    
    system_prompt = "Je bent een expert Nederlandse contentschrijver. ABSOLUUT VERBODEN: 'voordelen', 'voordeel' in ELKE vorm. Gebruik alternatieven zoals: pluspunten, sterke punten, wat het biedt, de meerwaarde."
    
    # Check if "Best of All" mode - use GPT-4.1 (best available model)
    if model == "best-of-all":
        print("🌟 Using Best of All mode - using GPT-4.1 (best model)")
        model = "gpt-4.1"
    
    # Check if Claude model
    is_claude = model.startswith('claude-')
    
    for attempt in range(max_retries):
        try:
            if is_claude:
                # Use Claude API
                if not anthropic_client:
                    raise Exception("Anthropic API key not configured")
                
                article = call_claude_api(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    model=model,
                    max_tokens=4000
                )
            else:
                # Use OpenAI API
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
                    article = re.sub(r'\bvoordelen\s+van\b', 'pluspunten van', article, flags=re.IGNORECASE)
                    article = re.sub(r'\bvoordeel\s+van\b', 'pluspunt van', article, flags=re.IGNORECASE)
                    article = re.sub(r'\bvoordelen\b', 'pluspunten', article, flags=re.IGNORECASE)
                    article = re.sub(r'\bvoordeel\b', 'pluspunt', article, flags=re.IGNORECASE)
                    article = re.sub(r'dat is best een opluchting,?\s*toch\??', 'dat is fijn om te weten', article, flags=re.IGNORECASE)
            
            article = re.sub(r'^H2:\s*conclusie\s*$', 'H2: Conclusie', article, flags=re.MULTILINE | re.IGNORECASE)
            
            # Process placeholders BEFORE formatting HTML
            article = process_article_placeholders(article, onderwerp, elements)
            article = format_article_html(article)
            
            print(f"✅ Article generated successfully with {model} (attempt {attempt + 1})")
            return article
            
        except Exception as e:
            print(f"API Error with {model} (attempt {attempt + 1}): {e}")
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
    
    # Check if "Best of All" mode - use GPT-4.1
    if model == "best-of-all":
        print("🌟 Using Best of All mode - using GPT-4.1 (best model)")
        model = "gpt-4.1"
    
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
        response = call_openai_with_correct_params(
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
                images = search_pixabay_images(search_query, per_page=1)
                if images:
                    img_url = images[0]['medium_url']
                    img_tag = f'<img src="{img_url}" alt="{search_query}" style="max-width: 100%; height: auto; margin: 20px 0;">'
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
                if result.get('success'):
                    img_url = result['image_url']
                    img_tag = f'<img src="{img_url}" alt="AI Generated: {prompt[:50]}" style="max-width: 100%; height: auto; margin: 20px 0;">'
                    article = article.replace(f'[AI-IMAGE: {match}]', img_tag, 1)
                else:
                    article = article.replace(f'[AI-IMAGE: {match}]', '', 1)
            except Exception as e:
                print(f"Error generating DALL-E image for '{prompt}': {e}")
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

def search_pixabay_images(query, per_page=10, image_type='photo', orientation='horizontal'):
    """
    Search for images on Pixabay
    
    Args:
        query: Search term
        per_page: Number of results (default 10, max 200)
        image_type: 'all', 'photo', 'illustration', 'vector'
        orientation: 'all', 'horizontal', 'vertical'
    
    Returns:
        List of image objects with URLs and metadata
    """
    if not PIXABAY_API_KEY:
        raise Exception("Pixabay API key not configured")
    
    try:
        url = "https://pixabay.com/api/"
        params = {
            'key': PIXABAY_API_KEY,
            'q': query,
            'per_page': min(per_page, 200),  # Max 200
            'image_type': image_type,
            'orientation': orientation,
            'safesearch': 'true',
            'lang': 'nl'
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('totalHits', 0) == 0:
            return []
        
        # Format results
        images = []
        for hit in data.get('hits', []):
            images.append({
                'id': hit.get('id'),
                'preview_url': hit.get('previewURL'),
                'small_url': hit.get('webformatURL'),  # 640px
                'medium_url': hit.get('largeImageURL'),  # 1280px
                'full_url': hit.get('fullHDURL') or hit.get('imageURL'),  # Full size
                'width': hit.get('imageWidth'),
                'height': hit.get('imageHeight'),
                'tags': hit.get('tags'),
                'user': hit.get('user'),
                'page_url': hit.get('pageURL')
            })
        
        return images
        
    except requests.exceptions.RequestException as e:
        print(f"Pixabay API Error: {e}")
        raise Exception(f"Failed to fetch images from Pixabay: {str(e)}")

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
        print("⚠️ Originality.AI API key not configured")
        return {
            "success": False,
            "ai_score": None,
            "human_score": None,
            "error": "API key not configured"
        }
    
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
        
        # Limit content length (Originality.AI has limits)
        if len(text_content) > 25000:
            text_content = text_content[:25000]
        
        payload = {
            "content": text_content,
            "title": "Article Scan",
            "aiModelVersion": "1"
        }
        
        print(f"📊 Checking originality with Originality.AI...")
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            ai_score = round(data.get('score', {}).get('ai', 0) * 100, 1)
            human_score = round(data.get('score', {}).get('original', 0) * 100, 1)
            print(f"✅ Originality check complete: AI={ai_score}%, Human={human_score}%")
            return {
                "success": True,
                "ai_score": ai_score,
                "human_score": human_score
            }
        else:
            error_msg = f"API Error: {response.status_code}"
            print(f"⚠️ Originality.AI error: {error_msg}")
            try:
                error_data = response.json()
                error_msg += f" - {error_data.get('message', '')}"
            except:
                pass
            return {
                "success": False,
                "ai_score": None,
                "human_score": None,
                "error": error_msg
            }
            
    except Exception as e:
        print(f"⚠️ Originality.AI exception: {str(e)}")
        return {
            "success": False,
            "ai_score": None,
            "human_score": None,
            "error": str(e)
        }

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

@app.route('/api/suggest-topic', methods=['POST'])
def api_suggest_topic():
    """Suggest topic based on URLs and anchors"""
    try:
        data = request.json
        anchor1 = data.get('anchor1', '').strip()
        url1 = data.get('url1', '').strip()
        anchor2 = data.get('anchor2', '').strip()
        url2 = data.get('url2', '').strip()
        context = data.get('context', '').strip()
        placement_domain = data.get('placement_domain', '').strip()
        
        if not all([anchor1, url1, anchor2, url2]):
            return jsonify({"error": "All anchors and URLs are required"}), 400
        
        topic = extract_topic_from_urls(anchor1, url1, anchor2, url2, context, placement_domain)
        
        if topic:
            return jsonify({"success": True, "topic": topic})
        else:
            return jsonify({"error": "Could not generate topic"}), 500
            
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
        placement_domain = data.get('placement_domain', '').strip()
        
        # Add domain analysis to extra context if provided
        if placement_domain:
            domain_analysis = analyze_placement_domain(placement_domain)
            if domain_analysis:
                extra += domain_analysis
        
        if not all([onderwerp, anchor1, url1, anchor2, url2]):
            return jsonify({"success": False, "error": "All fields are required"}), 400
        
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
        print(f"❌ Error in generate-article: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/generate-general-article', methods=['POST'])
def api_generate_general_article():
    """Generate general article with optional extra elements"""
    try:
        data = request.json
        onderwerp = data.get('onderwerp', '').strip()
        word_count = int(data.get('word_count', 500))
        extra = data.get('extra', '').strip()
        model = data.get('model', 'gpt-4o')
        use_research = data.get('use_research', False)  # NEW: Research toggle
        
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
        
        article = generate_general_article(onderwerp, word_count, extra, model, elements, use_research=use_research)
        
        # Count words
        text_content = re.sub(r'<[^>]+>', '', article)
        actual_word_count = len(text_content.split())
        
        return jsonify({
            "success": True,
            "article": article,
            "word_count": actual_word_count
        })
        
    except Exception as e:
        print(f"❌ Error in generate-general-article: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

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
        per_page = data.get('per_page', 10)
        image_type = data.get('image_type', 'photo')
        orientation = data.get('orientation', 'horizontal')
        
        if not query:
            return jsonify({"error": "Search query is required"}), 400
        
        images = search_pixabay_images(
            query=query,
            per_page=per_page,
            image_type=image_type,
            orientation=orientation
        )
        
        return jsonify({
            "success": True,
            "total": len(images),
            "images": images
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
