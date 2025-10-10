
"""
Automatische Blog Generator voor WritgoAI
Genereert complete blogs met afbeeldingen, interne links en affiliate links
"""

import json
import re
import requests
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator

class BlogGenerator:
    """
    Hoofdklasse voor automatische blog generatie
    Integreert afbeeldingen, interne links en affiliate links
    """
    
    def __init__(self, pixabay_api_key: str, pexels_api_key: Optional[str] = None, 
                 unsplash_access_key: Optional[str] = None):
        """
        Initialiseer de blog generator met API keys
        
        Args:
            pixabay_api_key: Pixabay API key (verplicht)
            pexels_api_key: Pexels API key (optioneel)
            unsplash_access_key: Unsplash access key (optioneel)
        """
        self.pixabay_api_key = pixabay_api_key
        self.pexels_api_key = pexels_api_key
        self.unsplash_access_key = unsplash_access_key
        
        # Image fetcher
        from image_fetcher import ImageFetcher
        self.image_fetcher = ImageFetcher(
            pixabay_api_key=pixabay_api_key,
            pexels_api_key=pexels_api_key,
            unsplash_access_key=unsplash_access_key
        )
        
        # Sitemap parser
        from sitemap_parser import SitemapParser
        self.sitemap_parser = SitemapParser()
        
        # Affiliate linker
        from affiliate_linker import AffiliateLinker
        self.affiliate_linker = AffiliateLinker()
        
        # Markdown generator
        from markdown_generator import MarkdownGenerator
        self.markdown_generator = MarkdownGenerator()
    
    def generate_blog(self, 
                     topic: str,
                     word_count: int,
                     website_url: str,
                     sitemap_url: Optional[str] = None,
                     affiliate_config: Optional[Dict] = None,
                     extra_context: str = "",
                     model: str = "gpt-4o") -> Dict:
        """
        Genereer een complete blog met alle features
        
        Args:
            topic: Blog onderwerp
            word_count: Gewenst aantal woorden
            website_url: URL van de website (voor interne links)
            sitemap_url: Directe sitemap URL (optioneel)
            affiliate_config: Affiliate configuratie per website
            extra_context: Extra context voor de blog
            model: AI model om te gebruiken
            
        Returns:
            Dict met success status, blog content en metadata
        """
        try:
            print(f"🚀 Starting blog generation for: {topic}")
            
            # Stap 1: Zoek relevante afbeeldingen
            print("📸 Step 1: Fetching images...")
            images = self._fetch_images_for_blog(topic, word_count)
            
            # Stap 2: Haal interne links op van de website
            print("🔗 Step 2: Extracting internal links...")
            internal_links = self._extract_internal_links(website_url, sitemap_url, topic)
            
            # Stap 3: Genereer affiliate links
            print("💰 Step 3: Generating affiliate links...")
            affiliate_links = self._generate_affiliate_links(topic, affiliate_config or {})
            
            # Stap 4: Genereer de blog content met AI
            print("✍️ Step 4: Generating blog content...")
            blog_content = self._generate_blog_content(
                topic=topic,
                word_count=word_count,
                images=images,
                internal_links=internal_links,
                affiliate_links=affiliate_links,
                extra_context=extra_context,
                model=model
            )
            
            # Stap 5: Converteer naar markdown formaat
            print("📝 Step 5: Converting to markdown...")
            markdown_content = self.markdown_generator.html_to_markdown(blog_content)
            
            print("✅ Blog generation completed successfully!")
            
            return {
                'success': True,
                'content': blog_content,
                'markdown': markdown_content,
                'metadata': {
                    'topic': topic,
                    'word_count': len(blog_content.split()),
                    'images_count': len(images),
                    'internal_links_count': len(internal_links),
                    'affiliate_links_count': len(affiliate_links)
                },
                'images': images,
                'internal_links': internal_links,
                'affiliate_links': affiliate_links
            }
            
        except Exception as e:
            print(f"❌ Error generating blog: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return {
                'success': False,
                'error': str(e)
            }
    
    def _fetch_images_for_blog(self, topic: str, word_count: int) -> List[Dict]:
        """
        Haal relevante afbeeldingen op voor de blog
        1 afbeelding per 500 woorden
        """
        num_images = max(1, word_count // 500)
        print(f"  → Fetching {num_images} images for {word_count} words")
        
        # Genereer zoektermen voor afbeeldingen
        search_queries = self._generate_image_search_queries(topic, num_images)
        
        images = []
        for query in search_queries:
            # Probeer eerst Pixabay
            result = self.image_fetcher.search_images(query, source='pixabay', limit=1)
            if result and result.get('images'):
                images.extend(result['images'])
            # Als Pixabay geen resultaten geeft, probeer Pexels
            elif self.pexels_api_key:
                result = self.image_fetcher.search_images(query, source='pexels', limit=1)
                if result and result.get('images'):
                    images.extend(result['images'])
            # Als laatste optie, probeer Unsplash
            elif self.unsplash_access_key:
                result = self.image_fetcher.search_images(query, source='unsplash', limit=1)
                if result and result.get('images'):
                    images.extend(result['images'])
        
        print(f"  ✓ Found {len(images)} images")
        return images[:num_images]
    
    def _generate_image_search_queries(self, topic: str, num_queries: int) -> List[str]:
        """
        Genereer relevante zoektermen voor afbeeldingen op basis van het onderwerp
        """
        # Vertaal topic naar Engels voor betere zoekresultaten
        try:
            translator = GoogleTranslator(source='auto', target='en')
            english_topic = translator.translate(topic)
        except:
            english_topic = topic
        
        # Basis query
        queries = [english_topic]
        
        # Voeg variaties toe
        variations = [
            f"{english_topic} travel",
            f"{english_topic} destination",
            f"{english_topic} tourism",
            f"{english_topic} vacation",
            f"{english_topic} holiday",
            f"{english_topic} city",
            f"{english_topic} landscape",
            f"{english_topic} architecture"
        ]
        
        queries.extend(variations[:num_queries - 1])
        return queries[:num_queries]
    
    def _extract_internal_links(self, website_url: str, sitemap_url: Optional[str], 
                                topic: str) -> List[Dict]:
        """
        Haal relevante interne links op van de website
        """
        # Parse sitemap
        sitemap_data = self.sitemap_parser.parse_sitemap(website_url, sitemap_url)
        
        if not sitemap_data.get('success'):
            print(f"  ⚠️ Could not parse sitemap: {sitemap_data.get('error')}")
            return []
        
        urls = sitemap_data.get('urls', [])
        print(f"  → Found {len(urls)} URLs in sitemap")
        
        # Filter relevante URLs op basis van het onderwerp
        relevant_links = self.sitemap_parser.find_relevant_urls(urls, topic, limit=10)
        
        print(f"  ✓ Found {len(relevant_links)} relevant internal links")
        return relevant_links
    
    def _generate_affiliate_links(self, topic: str, affiliate_config: Dict) -> List[Dict]:
        """
        Genereer relevante affiliate links op basis van het onderwerp
        """
        affiliate_links = self.affiliate_linker.generate_links(topic, affiliate_config)
        print(f"  ✓ Generated {len(affiliate_links)} affiliate links")
        return affiliate_links
    
    def _generate_blog_content(self, topic: str, word_count: int, images: List[Dict],
                               internal_links: List[Dict], affiliate_links: List[Dict],
                               extra_context: str, model: str) -> str:
        """
        Genereer de blog content met AI, inclusief afbeeldingen en links
        """
        # Importeer OpenAI client
        from openai import OpenAI
        import os
        
        # Lees OpenAI API key
        try:
            with open('/home/ubuntu/.config/abacusai_auth_secrets.json', 'r') as f:
                secrets = json.load(f)
                api_key = secrets.get('openai', {}).get('secrets', {}).get('api_key', {}).get('value')
        except:
            api_key = os.environ.get('OPENAI_API_KEY')
        
        if not api_key:
            raise Exception("OpenAI API key not found")
        
        client = OpenAI(api_key=api_key)
        
        # Bereid context voor
        images_context = self._format_images_context(images)
        internal_links_context = self._format_internal_links_context(internal_links)
        affiliate_links_context = self._format_affiliate_links_context(affiliate_links)
        
        # Maak de prompt
        prompt = f"""Schrijf een uitgebreide, professionele blog over: {topic}

VEREISTEN:
- Minimaal {word_count} woorden
- Gebruik HTML formatting (<h2>, <h3>, <p>, <ul>, <li>, etc.)
- Sentence case voor alle headings
- Professionele, informatieve toon
- Voeg een FAQ sectie toe met minimaal 5 vragen
- Voeg praktische tips toe waar relevant

AFBEELDINGEN (gebruik deze URLs in je blog):
{images_context}

INTERNE LINKS (verwijs naar deze pagina's waar relevant):
{internal_links_context}

AFFILIATE LINKS (voeg deze toe waar passend):
{affiliate_links_context}

EXTRA CONTEXT:
{extra_context}

STRUCTUUR:
1. Inleiding (met eerste afbeelding)
2. Hoofdsecties met subsecties (verdeel afbeeldingen gelijkmatig)
3. Praktische tips sectie
4. FAQ sectie
5. Conclusie

BELANGRIJK:
- Gebruik de afbeelding URLs in <img> tags: <img src="URL" alt="beschrijving">
- Voeg interne links toe als <a href="URL">anchor text</a>
- Voeg affiliate links toe als <a href="URL" target="_blank" rel="nofollow">anchor text</a>
- Zorg dat de content natuurlijk en leesbaar is
- Geen markdown code blocks, alleen HTML!
"""
        
        # Roep OpenAI API aan
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Je bent een expert Nederlandse contentschrijver gespecialiseerd in reisblogs en informatieve artikelen. Schrijf natuurlijk, boeiend en informatief."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=4000
        )
        
        content = response.choices[0].message.content
        
        # Clean up content
        content = self._clean_content(content)
        
        return content
    
    def _format_images_context(self, images: List[Dict]) -> str:
        """Format images voor de AI prompt"""
        if not images:
            return "Geen afbeeldingen beschikbaar"
        
        context = []
        for i, img in enumerate(images, 1):
            context.append(f"{i}. URL: {img.get('url')}")
            context.append(f"   Alt text: {img.get('description', img.get('tags', 'image'))}")
        
        return "\n".join(context)
    
    def _format_internal_links_context(self, links: List[Dict]) -> str:
        """Format interne links voor de AI prompt"""
        if not links:
            return "Geen interne links beschikbaar"
        
        context = []
        for i, link in enumerate(links, 1):
            context.append(f"{i}. {link.get('title', 'Link')} - {link.get('url')}")
        
        return "\n".join(context)
    
    def _format_affiliate_links_context(self, links: List[Dict]) -> str:
        """Format affiliate links voor de AI prompt"""
        if not links:
            return "Geen affiliate links beschikbaar"
        
        context = []
        for i, link in enumerate(links, 1):
            context.append(f"{i}. {link.get('anchor_text')} - {link.get('url')}")
        
        return "\n".join(context)
    
    def _clean_content(self, content: str) -> str:
        """
        Clean up de gegenereerde content
        Verwijder markdown code blocks en andere ongewenste formatting
        """
        # Verwijder markdown code blocks
        content = re.sub(r'```html\s*', '', content)
        content = re.sub(r'```markdown\s*', '', content)
        content = re.sub(r'```\s*', '', content)
        
        # Verwijder excessive whitespace
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # Trim
        content = content.strip()
        
        return content
