
"""
Sitemap Parser Module
Parse sitemaps en vind relevante interne links
"""

import requests
import xml.etree.ElementTree as ET
from urllib.parse import urljoin, urlparse
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
import re


class SitemapParser:
    """
    Klasse voor het parsen van sitemaps en vinden van relevante URLs
    """
    
    def parse_sitemap(self, website_url: str, sitemap_url: Optional[str] = None) -> Dict:
        """
        Parse de sitemap van een website
        
        Args:
            website_url: Base URL van de website
            sitemap_url: Directe sitemap URL (optioneel)
            
        Returns:
            Dict met success status en lijst van URLs
        """
        try:
            # Normaliseer website URL
            if not website_url.startswith(('http://', 'https://')):
                website_url = 'https://' + website_url
            
            parsed = urlparse(website_url)
            base_domain = f"{parsed.scheme}://{parsed.netloc}"
            
            # Als geen sitemap URL gegeven, probeer te detecteren
            if not sitemap_url:
                sitemap_url = self._detect_sitemap(base_domain)
                if not sitemap_url:
                    return {
                        'success': False,
                        'error': 'Could not detect sitemap'
                    }
            
            print(f"  → Parsing sitemap: {sitemap_url}")
            
            # Haal sitemap op
            response = requests.get(sitemap_url, timeout=15)
            
            if response.status_code != 200:
                return {
                    'success': False,
                    'error': f'Failed to fetch sitemap: {response.status_code}'
                }
            
            # Parse XML
            urls = self._parse_sitemap_xml(response.content, base_domain)
            
            return {
                'success': True,
                'urls': urls,
                'sitemap_url': sitemap_url
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error parsing sitemap: {str(e)}'
            }
    
    def _detect_sitemap(self, base_domain: str) -> Optional[str]:
        """
        Detecteer sitemap URL automatisch
        """
        # Probeer robots.txt eerst
        try:
            robots_url = urljoin(base_domain, '/robots.txt')
            response = requests.get(robots_url, timeout=10)
            
            if response.status_code == 200:
                for line in response.text.split('\n'):
                    if line.lower().startswith('sitemap:'):
                        sitemap_url = line.split(':', 1)[1].strip()
                        # Verifieer dat sitemap bestaat
                        verify = requests.head(sitemap_url, timeout=10)
                        if verify.status_code == 200:
                            return sitemap_url
        except:
            pass
        
        # Probeer common paths
        common_paths = [
            '/sitemap.xml',
            '/sitemap_index.xml',
            '/sitemap-index.xml',
            '/wp-sitemap.xml',
            '/sitemap1.xml'
        ]
        
        for path in common_paths:
            try:
                sitemap_url = urljoin(base_domain, path)
                response = requests.head(sitemap_url, timeout=10)
                if response.status_code == 200:
                    return sitemap_url
            except:
                continue
        
        return None
    
    def _parse_sitemap_xml(self, xml_content: bytes, base_domain: str) -> List[Dict]:
        """
        Parse sitemap XML en extraheer URLs
        """
        urls = []
        
        try:
            root = ET.fromstring(xml_content)
            
            # Namespace handling
            namespaces = {
                'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'
            }
            
            # Check if this is a sitemap index
            sitemap_elements = root.findall('.//sm:sitemap', namespaces)
            
            if sitemap_elements:
                # Dit is een sitemap index, parse alle sub-sitemaps
                for sitemap in sitemap_elements:
                    loc = sitemap.find('sm:loc', namespaces)
                    if loc is not None and loc.text:
                        sub_urls = self._parse_sub_sitemap(loc.text, base_domain)
                        urls.extend(sub_urls)
            else:
                # Dit is een reguliere sitemap
                url_elements = root.findall('.//sm:url', namespaces)
                
                for url_elem in url_elements:
                    loc = url_elem.find('sm:loc', namespaces)
                    if loc is not None and loc.text:
                        # Probeer titel te halen van de URL
                        title = self._extract_title_from_url(loc.text)
                        
                        urls.append({
                            'url': loc.text,
                            'title': title
                        })
        
        except ET.ParseError:
            # Als XML parsing faalt, probeer als HTML
            try:
                soup = BeautifulSoup(xml_content, 'html.parser')
                loc_tags = soup.find_all('loc')
                
                for loc in loc_tags:
                    if loc.text:
                        title = self._extract_title_from_url(loc.text)
                        urls.append({
                            'url': loc.text,
                            'title': title
                        })
            except:
                pass
        
        return urls
    
    def _parse_sub_sitemap(self, sitemap_url: str, base_domain: str) -> List[Dict]:
        """
        Parse een sub-sitemap
        """
        try:
            response = requests.get(sitemap_url, timeout=15)
            if response.status_code == 200:
                return self._parse_sitemap_xml(response.content, base_domain)
        except:
            pass
        
        return []
    
    def _extract_title_from_url(self, url: str) -> str:
        """
        Extraheer een leesbare titel van een URL
        """
        # Haal het laatste deel van de URL path
        parsed = urlparse(url)
        path = parsed.path.strip('/')
        
        if not path:
            return 'Homepage'
        
        # Neem het laatste segment
        segments = path.split('/')
        last_segment = segments[-1]
        
        # Verwijder extensies
        last_segment = re.sub(r'\.(html|php|aspx?)$', '', last_segment)
        
        # Vervang hyphens en underscores met spaties
        title = last_segment.replace('-', ' ').replace('_', ' ')
        
        # Capitalize
        title = title.title()
        
        return title
    
    def find_relevant_urls(self, urls: List[Dict], topic: str, limit: int = 10) -> List[Dict]:
        """
        Vind relevante URLs op basis van het onderwerp
        
        Args:
            urls: Lijst van URLs uit sitemap
            topic: Onderwerp om op te filteren
            limit: Maximum aantal URLs om te retourneren
            
        Returns:
            Lijst van relevante URLs
        """
        # Extraheer keywords uit het onderwerp
        keywords = self._extract_keywords(topic)
        
        # Score elke URL op relevantie
        scored_urls = []
        for url_data in urls:
            url = url_data.get('url', '')
            title = url_data.get('title', '')
            
            score = 0
            
            # Check URL en titel voor keywords
            url_lower = url.lower()
            title_lower = title.lower()
            
            for keyword in keywords:
                keyword_lower = keyword.lower()
                if keyword_lower in url_lower:
                    score += 2
                if keyword_lower in title_lower:
                    score += 3
            
            if score > 0:
                scored_urls.append({
                    'url': url,
                    'title': title,
                    'score': score
                })
        
        # Sorteer op score
        scored_urls.sort(key=lambda x: x['score'], reverse=True)
        
        # Return top results
        return scored_urls[:limit]
    
    def _extract_keywords(self, text: str) -> List[str]:
        """
        Extraheer keywords uit tekst
        """
        # Verwijder stopwoorden en split
        stopwords = {'de', 'het', 'een', 'en', 'van', 'in', 'op', 'met', 'voor', 
                    'naar', 'aan', 'bij', 'te', 'is', 'zijn', 'was', 'waren'}
        
        words = re.findall(r'\w+', text.lower())
        keywords = [w for w in words if w not in stopwords and len(w) > 2]
        
        return keywords
