
"""
Image Fetcher Module
Haalt afbeeldingen op van Pixabay, Pexels en Unsplash
"""

import requests
import json
from typing import Dict, List, Optional
from deep_translator import GoogleTranslator


class ImageFetcher:
    """
    Klasse voor het ophalen van afbeeldingen van verschillende bronnen
    """
    
    def __init__(self, pixabay_api_key: str, pexels_api_key: Optional[str] = None,
                 unsplash_access_key: Optional[str] = None):
        """
        Initialiseer de image fetcher met API keys
        
        Args:
            pixabay_api_key: Pixabay API key (verplicht)
            pexels_api_key: Pexels API key (optioneel)
            unsplash_access_key: Unsplash access key (optioneel)
        """
        self.pixabay_api_key = pixabay_api_key
        self.pexels_api_key = pexels_api_key
        self.unsplash_access_key = unsplash_access_key
    
    def search_images(self, query: str, source: str = 'pixabay', 
                     limit: int = 5) -> Dict:
        """
        Zoek afbeeldingen van de opgegeven bron
        
        Args:
            query: Zoekterm
            source: Bron (pixabay, pexels, unsplash)
            limit: Maximum aantal resultaten
            
        Returns:
            Dict met success status en lijst van afbeeldingen
        """
        # Vertaal query naar Engels voor betere resultaten
        try:
            translator = GoogleTranslator(source='auto', target='en')
            english_query = translator.translate(query)
        except:
            english_query = query
        
        print(f"  → Searching {source} for: {english_query}")
        
        if source == 'pixabay':
            return self._search_pixabay(english_query, limit)
        elif source == 'pexels':
            return self._search_pexels(english_query, limit)
        elif source == 'unsplash':
            return self._search_unsplash(english_query, limit)
        else:
            return {'success': False, 'error': f'Unknown source: {source}'}
    
    def _search_pixabay(self, query: str, limit: int) -> Dict:
        """Zoek afbeeldingen op Pixabay"""
        if not self.pixabay_api_key:
            return {'success': False, 'error': 'Pixabay API key not configured'}
        
        try:
            url = "https://pixabay.com/api/"
            params = {
                'key': self.pixabay_api_key,
                'q': query,
                'per_page': min(limit, 20),
                'image_type': 'photo',
                'lang': 'en',
                'safesearch': 'true'
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code != 200:
                return {
                    'success': False,
                    'error': f'Pixabay API error: {response.status_code}'
                }
            
            data = response.json()
            
            images = []
            for hit in data.get('hits', [])[:limit]:
                images.append({
                    'url': hit.get('largeImageURL'),
                    'preview': hit.get('previewURL'),
                    'width': hit.get('imageWidth'),
                    'height': hit.get('imageHeight'),
                    'tags': hit.get('tags'),
                    'description': hit.get('tags', '').replace(',', ' '),
                    'source': 'pixabay',
                    'photographer': hit.get('user'),
                    'photographer_url': f"https://pixabay.com/users/{hit.get('user')}-{hit.get('user_id')}/"
                })
            
            return {
                'success': True,
                'images': images,
                'total': data.get('totalHits', 0)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Pixabay error: {str(e)}'
            }
    
    def _search_pexels(self, query: str, limit: int) -> Dict:
        """Zoek afbeeldingen op Pexels"""
        if not self.pexels_api_key:
            return {'success': False, 'error': 'Pexels API key not configured'}
        
        try:
            url = "https://api.pexels.com/v1/search"
            headers = {
                'Authorization': self.pexels_api_key
            }
            params = {
                'query': query,
                'per_page': min(limit, 80)
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code != 200:
                return {
                    'success': False,
                    'error': f'Pexels API error: {response.status_code}'
                }
            
            data = response.json()
            
            images = []
            for photo in data.get('photos', [])[:limit]:
                images.append({
                    'url': photo.get('src', {}).get('large'),
                    'preview': photo.get('src', {}).get('medium'),
                    'width': photo.get('width'),
                    'height': photo.get('height'),
                    'description': photo.get('alt', query),
                    'source': 'pexels',
                    'photographer': photo.get('photographer'),
                    'photographer_url': photo.get('photographer_url')
                })
            
            return {
                'success': True,
                'images': images,
                'total': data.get('total_results', 0)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Pexels error: {str(e)}'
            }
    
    def _search_unsplash(self, query: str, limit: int) -> Dict:
        """Zoek afbeeldingen op Unsplash"""
        if not self.unsplash_access_key:
            return {'success': False, 'error': 'Unsplash access key not configured'}
        
        try:
            url = "https://api.unsplash.com/search/photos"
            headers = {
                'Authorization': f'Client-ID {self.unsplash_access_key}'
            }
            params = {
                'query': query,
                'per_page': min(limit, 30)
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code != 200:
                return {
                    'success': False,
                    'error': f'Unsplash API error: {response.status_code}'
                }
            
            data = response.json()
            
            images = []
            for photo in data.get('results', [])[:limit]:
                images.append({
                    'url': photo.get('urls', {}).get('regular'),
                    'preview': photo.get('urls', {}).get('small'),
                    'width': photo.get('width'),
                    'height': photo.get('height'),
                    'description': photo.get('description', photo.get('alt_description', query)),
                    'source': 'unsplash',
                    'photographer': photo.get('user', {}).get('name'),
                    'photographer_url': photo.get('user', {}).get('links', {}).get('html')
                })
            
            return {
                'success': True,
                'images': images,
                'total': data.get('total', 0)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Unsplash error: {str(e)}'
            }
