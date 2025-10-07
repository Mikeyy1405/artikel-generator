from flask import Flask, render_template, request, jsonify
import openai
import os
import re
from urllib.parse import urlparse, parse_qs

app = Flask(__name__)

# OpenAI API Key
openai.api_key = os.getenv('OPENAI_API_KEY', 'your-api-key-here')

def extract_youtube_id(url):
    """Extract YouTube video ID from URL"""
    parsed_url = urlparse(url)
    
    if 'youtube.com' in parsed_url.netloc:
        query_params = parse_qs(parsed_url.query)
        return query_params.get('v', [None])[0]
    elif 'youtu.be' in parsed_url.netloc:
        return parsed_url.path.strip('/')
    
    return None

def create_youtube_embed(video_id):
    """Create YouTube embed HTML"""
    return f'''
    <div class="youtube-embed">
        <iframe src="https://www.youtube.com/embed/{video_id}" 
                frameborder="0" 
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                allowfullscreen>
        </iframe>
    </div>
    '''

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/generate-seo-article', methods=['POST'])
def api_generate_seo_article():
    try:
        data = request.json
        topic = data.get('topic')
        words = int(data.get('words', 800))
        keyword = data.get('keyword')
        title = data.get('title')
        meta = data.get('meta')
        
        if not all([topic, keyword, title, meta]):
            return jsonify({'success': False, 'error': 'Alle velden zijn verplicht'})
        
        prompt = f"""Schrijf een SEO-geoptimaliseerd artikel in HTML formaat.

ONDERWERP: {topic}
AANTAL WOORDEN: {words}
HOOFD KEYWORD: {keyword}
SEO TITEL: {title}
META BESCHRIJVING: {meta}

INSTRUCTIES:
1. Gebruik de SEO titel als H1 heading
2. Gebruik het hoofd keyword natuurlijk door het artikel (2-3% keyword density)
3. Maak gebruik van H2 en H3 subheadings
4. Schrijf in duidelijke, korte paragrafen
5. Gebruik HTML tags: <h1>, <h2>, <h3>, <p>, <strong>, <em>, <ul>, <ol>, <li>
6. Maak het artikel informatief en waardevol voor de lezer
7. Gebruik GEEN markdown, alleen HTML
8. Gebruik echte HTML lijsten met <ul> en <li> tags, GEEN markdown bullets

FORMAAT:
<h1>{title}</h1>

<p>Inleiding met het keyword...</p>

<h2>Eerste Sectie</h2>
<p>Content...</p>

<ul>
<li>Lijst item 1</li>
<li>Lijst item 2</li>
</ul>

<h2>Tweede Sectie</h2>
<p>Content...</p>

<p><strong>Conclusie</strong></p>

Schrijf nu het artikel:"""

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Je bent een expert SEO content schrijver. Je schrijft alleen in HTML formaat, NOOIT in markdown. Gebruik altijd HTML tags zoals <ul>, <li>, <p>, <h2>, etc."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=words * 2
        )
        
        article = response.choices[0].message.content.strip()
        
        # Ensure proper HTML formatting
        article = article.replace('**', '')
        article = article.replace('- ', '<li>').replace('\n<li>', '</li>\n<li>')
        
        return jsonify({
            'success': True,
            'article': article
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/generate-perplexity-article', methods=['POST'])
def api_generate_perplexity_article():
    try:
        data = request.json
        topic = data.get('topic')
        words = int(data.get('words', 800))
        
        if not topic:
            return jsonify({'success': False, 'error': 'Onderwerp is verplicht'})
        
        prompt = f"""Schrijf een diepgaand, goed onderbouwd artikel in HTML formaat.

ONDERWERP: {topic}
AANTAL WOORDEN: {words}

INSTRUCTIES:
1. Doe alsof je toegang hebt tot actuele informatie en research
2. Schrijf een informatief, feitelijk artikel
3. Gebruik H1 voor de titel, H2 en H3 voor subheadings
4. Gebruik HTML tags: <h1>, <h2>, <h3>, <p>, <strong>, <em>, <ul>, <ol>, <li>
5. Maak gebruik van lijsten waar relevant
6. Gebruik GEEN markdown, alleen HTML
7. Gebruik echte HTML lijsten met <ul> en <li> tags

Schrijf het artikel:"""

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Je bent een expert research schrijver. Je schrijft alleen in HTML formaat, NOOIT in markdown."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=words * 2
        )
        
        article = response.choices[0].message.content.strip()
        
        return jsonify({
            'success': True,
            'article': article
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/generate-youtube-post', methods=['POST'])
def api_generate_youtube_post():
    try:
        data = request.json
        url = data.get('url')
        topic = data.get('topic')
        words = int(data.get('words', 500))
        
        if not all([url, topic]):
            return jsonify({'success': False, 'error': 'Alle velden zijn verplicht'})
        
        # Extract YouTube ID
        video_id = extract_youtube_id(url)
        
        if not video_id:
            return jsonify({'success': False, 'error': 'Ongeldige YouTube URL'})
        
        # Create embed code
        embed_html = create_youtube_embed(video_id)
        
        prompt = f"""Schrijf een boeiende post over deze YouTube video in HTML formaat.

ONDERWERP: {topic}
AANTAL WOORDEN: {words}

INSTRUCTIES:
1. Schrijf een pakkende titel (H1)
2. Schrijf een inleiding die nieuwsgierig maakt
3. Bespreek wat kijkers kunnen verwachten
4. Gebruik HTML tags: <h1>, <h2>, <p>, <strong>, <em>, <ul>, <li>
5. Gebruik GEEN markdown, alleen HTML
6. Gebruik echte HTML lijsten met <ul> en <li> tags

Schrijf de post (zonder de video embed, die wordt automatisch toegevoegd):"""

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Je bent een expert content schrijver voor social media en blogs. Je schrijft alleen in HTML formaat."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=words * 2
        )
        
        article = response.choices[0].message.content.strip()
        
        # Insert video embed after the first paragraph
        paragraphs = article.split('</p>')
        if len(paragraphs) > 1:
            article = paragraphs[0] + '</p>' + embed_html + '</p>'.join(paragraphs[1:])
        else:
            article = article + embed_html
        
        return jsonify({
            'success': True,
            'article': article
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/generate-list-article', methods=['POST'])
def api_generate_list_article():
    try:
        data = request.json
        topic = data.get('topic')
        items = int(data.get('items', 10))
        words = int(data.get('words', 100))
        
        if not topic:
            return jsonify({'success': False, 'error': 'Onderwerp is verplicht'})
        
        prompt = f"""Schrijf een lijst artikel in HTML formaat.

ONDERWERP: {topic}
AANTAL ITEMS: {items}
WOORDEN PER ITEM: ongeveer {words}

INSTRUCTIES:
1. Maak een pakkende titel (H1)
2. Schrijf een korte inleiding
3. Maak een genummerde lijst met {items} items
4. Elk item heeft een H3 heading en uitleg
5. Gebruik HTML tags: <h1>, <h2>, <h3>, <p>, <strong>, <em>, <ol>, <li>
6. Gebruik GEEN markdown, alleen HTML
7. Gebruik echte HTML genummerde lijst met <ol> en <li> tags

FORMAAT:
<h1>Titel</h1>
<p>Inleiding...</p>

<ol>
<li>
<h3>1. Item Titel</h3>
<p>Uitleg over dit item...</p>
</li>
<li>
<h3>2. Item Titel</h3>
<p>Uitleg over dit item...</p>
</li>
</ol>

<p><strong>Conclusie</strong></p>

Schrijf het artikel:"""

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Je bent een expert content schrijver. Je schrijft alleen in HTML formaat, NOOIT in markdown."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=(words * items) + 500
        )
        
        article = response.choices[0].message.content.strip()
        
        return jsonify({
            'success': True,
            'article': article
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/modify-article', methods=['POST'])
def api_modify_article():
    try:
        data = request.json
        content = data.get('content')
        instruction = data.get('instruction')
        
        if not all([content, instruction]):
            return jsonify({'success': False, 'error': 'Content en instructie zijn verplicht'})
        
        prompt = f"""Je krijgt een HTML artikel en een instructie om het aan te passen.

HUIDIGE ARTIKEL:
{content}

INSTRUCTIE:
{instruction}

Pas het artikel aan volgens de instructie. Behoud de HTML formatting. Gebruik GEEN markdown, alleen HTML tags.
Geef alleen het aangepaste artikel terug, geen uitleg."""

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Je bent een expert editor. Je past artikelen aan volgens instructies. Je gebruikt alleen HTML formaat, NOOIT markdown."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=3000
        )
        
        modified_content = response.choices[0].message.content.strip()
        
        return jsonify({
            'success': True,
            'modified_content': modified_content,
            'response': 'Artikel is aangepast!'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
