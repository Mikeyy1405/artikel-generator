
"""
Pixabay API Integration Module
Complete implementation volgens officiële Pixabay API documentatie
Ondersteunt zowel afbeeldingen als video's
"""

import requests
from typing import Dict, List, Optional, Any
import time


class PixabayAPI:
    """
    Pixabay API client voor het zoeken van afbeeldingen en video's
    
    API Documentatie: https://pixabay.com/api/docs/
    Rate Limit: 100 requests per 60 seconden (standaard)
    """
    
    BASE_URL_IMAGES = "https://pixabay.com/api/"
    BASE_URL_VIDEOS = "https://pixabay.com/api/videos/"
    
    def __init__(self, api_key: str):
        """
        Initialiseer Pixabay API client
        
        Args:
            api_key: Pixabay API key
        """
        if not api_key:
            raise ValueError("Pixabay API key is verplicht")
        
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; ArtikelGenerator/1.0)'
        })
    
    def search_images(
        self,
        query: str = "",
        lang: str = "nl",
        image_type: str = "photo",
        orientation: str = "horizontal",
        category: Optional[str] = None,
        min_width: int = 0,
        min_height: int = 0,
        colors: Optional[str] = None,
        editors_choice: bool = False,
        safesearch: bool = True,
        order: str = "popular",
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """
        Zoek afbeeldingen op Pixabay
        
        Args:
            query: Zoekterm (max 100 karakters, URL encoded)
            lang: Taalcode (nl, en, de, etc.)
            image_type: Type afbeelding - "all", "photo", "illustration", "vector"
            orientation: Oriëntatie - "all", "horizontal", "vertical"
            category: Categorie filter (backgrounds, fashion, nature, etc.)
            min_width: Minimale breedte in pixels
            min_height: Minimale hoogte in pixels
            colors: Kleurfilter (comma separated: "red,blue,green")
            editors_choice: Alleen Editor's Choice afbeeldingen
            safesearch: Alleen veilige content
            order: Sortering - "popular" of "latest"
            page: Paginanummer (start bij 1)
            per_page: Resultaten per pagina (3-200)
        
        Returns:
            Dict met 'success', 'data' (bij succes) of 'error' (bij fout)
        """
        # Valideer parameters
        if len(query) > 100:
            return {
                'success': False,
                'error': 'Zoekterm mag maximaal 100 karakters bevatten'
            }
        
        if per_page < 3 or per_page > 200:
            per_page = min(max(per_page, 3), 200)
        
        # Bouw parameters
        params = {
            'key': self.api_key,
            'q': query,
            'lang': lang,
            'image_type': image_type,
            'orientation': orientation,
            'safesearch': 'true' if safesearch else 'false',
            'order': order,
            'page': page,
            'per_page': per_page
        }
        
        # Optionele parameters
        if category:
            params['category'] = category
        if min_width > 0:
            params['min_width'] = min_width
        if min_height > 0:
            params['min_height'] = min_height
        if colors:
            params['colors'] = colors
        if editors_choice:
            params['editors_choice'] = 'true'
        
        return self._make_request(self.BASE_URL_IMAGES, params, 'images')
    
    def search_videos(
        self,
        query: str = "",
        lang: str = "nl",
        video_type: str = "all",
        category: Optional[str] = None,
        min_width: int = 0,
        min_height: int = 0,
        editors_choice: bool = False,
        safesearch: bool = True,
        order: str = "popular",
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """
        Zoek video's op Pixabay
        
        Args:
            query: Zoekterm (max 100 karakters, URL encoded)
            lang: Taalcode (nl, en, de, etc.)
            video_type: Type video - "all", "film", "animation"
            category: Categorie filter (backgrounds, fashion, nature, etc.)
            min_width: Minimale breedte in pixels
            min_height: Minimale hoogte in pixels
            editors_choice: Alleen Editor's Choice video's
            safesearch: Alleen veilige content
            order: Sortering - "popular" of "latest"
            page: Paginanummer (start bij 1)
            per_page: Resultaten per pagina (3-200)
        
        Returns:
            Dict met 'success', 'data' (bij succes) of 'error' (bij fout)
        """
        # Valideer parameters
        if len(query) > 100:
            return {
                'success': False,
                'error': 'Zoekterm mag maximaal 100 karakters bevatten'
            }
        
        if per_page < 3 or per_page > 200:
            per_page = min(max(per_page, 3), 200)
        
        # Bouw parameters
        params = {
            'key': self.api_key,
            'q': query,
            'lang': lang,
            'video_type': video_type,
            'safesearch': 'true' if safesearch else 'false',
            'order': order,
            'page': page,
            'per_page': per_page
        }
        
        # Optionele parameters
        if category:
            params['category'] = category
        if min_width > 0:
            params['min_width'] = min_width
        if min_height > 0:
            params['min_height'] = min_height
        if editors_choice:
            params['editors_choice'] = 'true'
        
        return self._make_request(self.BASE_URL_VIDEOS, params, 'videos')
    
    def get_image_by_id(self, image_id: int) -> Dict[str, Any]:
        """
        Haal specifieke afbeelding op via ID
        
        Args:
            image_id: Pixabay afbeelding ID
        
        Returns:
            Dict met 'success', 'data' (bij succes) of 'error' (bij fout)
        """
        params = {
            'key': self.api_key,
            'id': str(image_id)
        }
        
        return self._make_request(self.BASE_URL_IMAGES, params, 'images')
    
    def get_video_by_id(self, video_id: int) -> Dict[str, Any]:
        """
        Haal specifieke video op via ID
        
        Args:
            video_id: Pixabay video ID
        
        Returns:
            Dict met 'success', 'data' (bij succes) of 'error' (bij fout)
        """
        params = {
            'key': self.api_key,
            'id': str(video_id)
        }
        
        return self._make_request(self.BASE_URL_VIDEOS, params, 'videos')
    
    def _make_request(
        self,
        url: str,
        params: Dict[str, Any],
        content_type: str
    ) -> Dict[str, Any]:
        """
        Voer API request uit met error handling
        
        Args:
            url: API endpoint URL
            params: Query parameters
            content_type: Type content ('images' of 'videos')
        
        Returns:
            Dict met 'success', 'data' (bij succes) of 'error' (bij fout)
        """
        try:
            print(f"🔍 Pixabay API request: {content_type} - query: '{params.get('q', 'all')}'")
            
            response = self.session.get(
                url,
                params=params,
                timeout=30
            )
            
            # Check rate limit headers
            rate_limit = response.headers.get('X-RateLimit-Limit')
            rate_remaining = response.headers.get('X-RateLimit-Remaining')
            rate_reset = response.headers.get('X-RateLimit-Reset')
            
            if rate_limit:
                print(f"📊 Rate limit: {rate_remaining}/{rate_limit} (reset in {rate_reset}s)")
            
            # Check HTTP status
            if response.status_code == 429:
                return {
                    'success': False,
                    'error': 'API rate limit bereikt. Probeer het later opnieuw.',
                    'rate_limit_exceeded': True
                }
            
            if response.status_code == 400:
                return {
                    'success': False,
                    'error': f'Ongeldige API request: {response.text}'
                }
            
            if response.status_code == 403:
                return {
                    'success': False,
                    'error': 'API key is ongeldig of heeft geen toegang'
                }
            
            if response.status_code != 200:
                return {
                    'success': False,
                    'error': f'API error (status {response.status_code}): {response.text}'
                }
            
            # Parse JSON response
            try:
                data = response.json()
            except ValueError as e:
                # Dit is de oorzaak van "Unexpected token '<'" - geen JSON response
                return {
                    'success': False,
                    'error': f'API retourneerde geen geldige JSON. Response: {response.text[:200]}'
                }
            
            # Verwerk resultaten
            total = data.get('total', 0)
            total_hits = data.get('totalHits', 0)
            hits = data.get('hits', [])
            
            print(f"✅ Pixabay: {len(hits)} resultaten gevonden (totaal: {total_hits})")
            
            # Format resultaten
            formatted_results = []
            
            if content_type == 'images':
                formatted_results = self._format_image_results(hits)
            elif content_type == 'videos':
                formatted_results = self._format_video_results(hits)
            
            return {
                'success': True,
                'data': {
                    'total': total,
                    'totalHits': total_hits,
                    'hits': formatted_results,
                    'count': len(formatted_results)
                }
            }
        
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': 'API request timeout - probeer het opnieuw'
            }
        
        except requests.exceptions.ConnectionError:
            return {
                'success': False,
                'error': 'Kan geen verbinding maken met Pixabay API'
            }
        
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'Request error: {str(e)}'
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': f'Onverwachte fout: {str(e)}'
            }
    
    def _format_image_results(self, hits: List[Dict]) -> List[Dict]:
        """
        Format image results voor consistente output
        
        Args:
            hits: Raw API hits
        
        Returns:
            Lijst met geformatteerde afbeelding data
        """
        formatted = []
        
        for hit in hits:
            formatted.append({
                'id': hit.get('id'),
                'type': hit.get('type', 'photo'),
                'tags': hit.get('tags', ''),
                'pageURL': hit.get('pageURL'),
                
                # Verschillende afbeelding groottes
                'previewURL': hit.get('previewURL'),
                'previewWidth': hit.get('previewWidth'),
                'previewHeight': hit.get('previewHeight'),
                
                'webformatURL': hit.get('webformatURL'),  # 640px
                'webformatWidth': hit.get('webformatWidth'),
                'webformatHeight': hit.get('webformatHeight'),
                
                'largeImageURL': hit.get('largeImageURL'),  # 1280px
                
                # Full resolution (alleen met approved account)
                'fullHDURL': hit.get('fullHDURL'),  # 1920px
                'imageURL': hit.get('imageURL'),  # Original
                'vectorURL': hit.get('vectorURL'),  # Vector (indien beschikbaar)
                
                'imageWidth': hit.get('imageWidth'),
                'imageHeight': hit.get('imageHeight'),
                'imageSize': hit.get('imageSize'),
                
                # Statistieken
                'views': hit.get('views', 0),
                'downloads': hit.get('downloads', 0),
                'likes': hit.get('likes', 0),
                'comments': hit.get('comments', 0),
                
                # Gebruiker info
                'user_id': hit.get('user_id'),
                'user': hit.get('user'),
                'userImageURL': hit.get('userImageURL')
            })
        
        return formatted
    
    def _format_video_results(self, hits: List[Dict]) -> List[Dict]:
        """
        Format video results voor consistente output
        
        Args:
            hits: Raw API hits
        
        Returns:
            Lijst met geformatteerde video data
        """
        formatted = []
        
        for hit in hits:
            videos_data = hit.get('videos', {})
            
            formatted.append({
                'id': hit.get('id'),
                'type': hit.get('type', 'film'),
                'tags': hit.get('tags', ''),
                'pageURL': hit.get('pageURL'),
                'duration': hit.get('duration', 0),
                
                # Video streams in verschillende groottes
                'videos': {
                    'large': self._format_video_stream(videos_data.get('large', {})),
                    'medium': self._format_video_stream(videos_data.get('medium', {})),
                    'small': self._format_video_stream(videos_data.get('small', {})),
                    'tiny': self._format_video_stream(videos_data.get('tiny', {}))
                },
                
                # Statistieken
                'views': hit.get('views', 0),
                'downloads': hit.get('downloads', 0),
                'likes': hit.get('likes', 0),
                'comments': hit.get('comments', 0),
                
                # Gebruiker info
                'user_id': hit.get('user_id'),
                'user': hit.get('user'),
                'userImageURL': hit.get('userImageURL')
            })
        
        return formatted
    
    def _format_video_stream(self, stream: Dict) -> Dict:
        """
        Format video stream data
        
        Args:
            stream: Raw stream data
        
        Returns:
            Geformatteerde stream data
        """
        return {
            'url': stream.get('url', ''),
            'width': stream.get('width', 0),
            'height': stream.get('height', 0),
            'size': stream.get('size', 0),
            'thumbnail': stream.get('thumbnail', '')
        }


# Convenience functies voor backward compatibility
def search_pixabay_images(
    api_key: str,
    query: str,
    per_page: int = 10,
    image_type: str = 'photo',
    orientation: str = 'horizontal'
) -> List[Dict]:
    """
    Eenvoudige functie voor het zoeken van afbeeldingen
    
    Args:
        api_key: Pixabay API key
        query: Zoekterm
        per_page: Aantal resultaten
        image_type: Type afbeelding
        orientation: Oriëntatie
    
    Returns:
        Lijst met afbeeldingen of lege lijst bij fout
    """
    try:
        client = PixabayAPI(api_key)
        result = client.search_images(
            query=query,
            per_page=per_page,
            image_type=image_type,
            orientation=orientation
        )
        
        if result['success']:
            return result['data']['hits']
        else:
            print(f"❌ Fout bij zoeken naar afbeeldingen: {result['error']}")
            return []
    
    except Exception as e:
        print(f"❌ Onverwachte fout: {str(e)}")
        return []


def search_pixabay_videos(
    api_key: str,
    query: str,
    per_page: int = 10,
    video_type: str = 'all'
) -> List[Dict]:
    """
    Eenvoudige functie voor het zoeken van video's
    
    Args:
        api_key: Pixabay API key
        query: Zoekterm
        per_page: Aantal resultaten
        video_type: Type video
    
    Returns:
        Lijst met video's of lege lijst bij fout
    """
    try:
        client = PixabayAPI(api_key)
        result = client.search_videos(
            query=query,
            per_page=per_page,
            video_type=video_type
        )
        
        if result['success']:
            return result['data']['hits']
        else:
            print(f"❌ Fout bij zoeken naar video's: {result['error']}")
            return []
    
    except Exception as e:
        print(f"❌ Onverwachte fout: {str(e)}")
        return []
