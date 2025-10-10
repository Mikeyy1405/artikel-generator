
"""
Affiliate Linker Module
Genereert affiliate links voor verschillende platforms
"""

from typing import Dict, List
import re


class AffiliateLinker:
    """
    Klasse voor het genereren van affiliate links
    """
    
    # Default affiliate configuraties
    DEFAULT_AFFILIATES = {
        'booking.com': {
            'base_url': 'https://www.booking.com/searchresults.html',
            'params': {
                'aid': '1234567',  # Placeholder - moet geconfigureerd worden
                'ss': '{destination}'
            }
        },
        'getyourguide': {
            'base_url': 'https://www.getyourguide.com/s/',
            'params': {
                'partner_id': '12345',  # Placeholder - moet geconfigureerd worden
                'q': '{destination}'
            }
        },
        'viator': {
            'base_url': 'https://www.viator.com/searchResults/all',
            'params': {
                'pid': '12345',  # Placeholder - moet geconfigureerd worden
                'text': '{destination}'
            }
        },
        'rentalcars': {
            'base_url': 'https://www.rentalcars.com/SearchResults.do',
            'params': {
                'affiliateCode': '12345',  # Placeholder - moet geconfigureerd worden
                'city': '{destination}'
            }
        }
    }
    
    def __init__(self):
        """Initialiseer de affiliate linker"""
        pass
    
    def generate_links(self, topic: str, config: Dict) -> List[Dict]:
        """
        Genereer affiliate links op basis van het onderwerp
        
        Args:
            topic: Blog onderwerp
            config: Affiliate configuratie per website
            
        Returns:
            Lijst van affiliate links
        """
        links = []
        
        # Extraheer bestemming uit het onderwerp
        destination = self._extract_destination(topic)
        
        if not destination:
            return links
        
        # Merge default config met user config
        affiliate_config = {**self.DEFAULT_AFFILIATES}
        
        # Update met user configuratie
        for platform, user_config in config.items():
            if platform in affiliate_config:
                affiliate_config[platform].update(user_config)
            else:
                affiliate_config[platform] = user_config
        
        # Genereer links voor elk platform
        for platform, platform_config in affiliate_config.items():
            link = self._generate_platform_link(platform, platform_config, destination, topic)
            if link:
                links.append(link)
        
        return links
    
    def _extract_destination(self, topic: str) -> str:
        """
        Extraheer de bestemming uit het onderwerp
        """
        # Simpele extractie - kan verbeterd worden met NLP
        # Zoek naar plaatsnamen, landen, etc.
        
        # Verwijder common woorden
        stopwords = ['met', 'kinderen', 'blog', 'tips', 'gids', 'vakantie', 
                    'reis', 'bezoeken', 'romantisch', 'weekend']
        
        words = topic.lower().split()
        destination_words = [w for w in words if w not in stopwords]
        
        if destination_words:
            # Neem het eerste woord als bestemming (vaak de plaatsnaam)
            return destination_words[0].capitalize()
        
        return topic
    
    def _generate_platform_link(self, platform: str, config: Dict, 
                                destination: str, topic: str) -> Dict:
        """
        Genereer een affiliate link voor een specifiek platform
        """
        try:
            base_url = config.get('base_url', '')
            params = config.get('params', {})
            
            if not base_url:
                return None
            
            # Vervang placeholders in params
            formatted_params = {}
            for key, value in params.items():
                if isinstance(value, str):
                    value = value.replace('{destination}', destination)
                    value = value.replace('{topic}', topic)
                formatted_params[key] = value
            
            # Bouw URL
            param_string = '&'.join([f"{k}={v}" for k, v in formatted_params.items()])
            full_url = f"{base_url}?{param_string}"
            
            # Genereer anchor text
            anchor_text = self._generate_anchor_text(platform, destination)
            
            return {
                'platform': platform,
                'url': full_url,
                'anchor_text': anchor_text,
                'type': 'affiliate'
            }
            
        except Exception as e:
            print(f"  ⚠️ Error generating {platform} link: {str(e)}")
            return None
    
    def _generate_anchor_text(self, platform: str, destination: str) -> str:
        """
        Genereer natuurlijke anchor text voor een affiliate link
        """
        templates = {
            'booking.com': [
                f"Boek je hotel in {destination}",
                f"Vind accommodatie in {destination}",
                f"Hotels in {destination}"
            ],
            'getyourguide': [
                f"Boek tours in {destination}",
                f"Activiteiten in {destination}",
                f"Excursies in {destination}"
            ],
            'viator': [
                f"Ontdek tours in {destination}",
                f"Boek activiteiten in {destination}",
                f"Rondleidingen in {destination}"
            ],
            'rentalcars': [
                f"Huur een auto in {destination}",
                f"Autoverhuur in {destination}",
                f"Vergelijk autoverhuur in {destination}"
            ]
        }
        
        platform_templates = templates.get(platform, [f"Bezoek {platform}"])
        
        # Kies de eerste template
        return platform_templates[0] if platform_templates else f"Bezoek {platform}"
