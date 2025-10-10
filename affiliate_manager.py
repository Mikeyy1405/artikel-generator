
"""
Affiliate Manager Module
Beheert affiliate links en feeds per website
Flexibel voor elke niche (reizen, e-commerce, software, etc.)
"""

import sqlite3
import json
import requests
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from urllib.parse import urlparse
import re


class AffiliateManager:
    """
    Klasse voor het beheren van affiliate links en feeds per website
    """
    
    def __init__(self, db_path: str = 'writgo_content.db'):
        """
        Initialiseer de affiliate manager
        
        Args:
            db_path: Pad naar de SQLite database
        """
        self.db_path = db_path
        self._init_tables()
    
    def _init_tables(self):
        """Initialiseer de database tabellen voor affiliate management"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Affiliate links tabel (uitgebreid)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS website_affiliate_links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                website_id INTEGER NOT NULL,
                anchor_text TEXT NOT NULL,
                url TEXT NOT NULL,
                category TEXT,
                priority INTEGER DEFAULT 0,
                link_type TEXT DEFAULT 'direct',
                notes TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (website_id) REFERENCES websites(id) ON DELETE CASCADE
            )
        ''')
        
        # Affiliate feeds tabel
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS website_affiliate_feeds (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                website_id INTEGER NOT NULL,
                feed_name TEXT NOT NULL,
                feed_url TEXT NOT NULL,
                feed_type TEXT DEFAULT 'xml',
                update_frequency TEXT DEFAULT 'daily',
                last_updated TIMESTAMP,
                product_count INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (website_id) REFERENCES websites(id) ON DELETE CASCADE
            )
        ''')
        
        # Feed products cache tabel
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feed_products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                feed_id INTEGER NOT NULL,
                product_id TEXT,
                product_name TEXT,
                product_url TEXT,
                product_price TEXT,
                product_category TEXT,
                product_image TEXT,
                product_description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (feed_id) REFERENCES website_affiliate_feeds(id) ON DELETE CASCADE
            )
        ''')
        
        conn.commit()
        conn.close()
    
    # ==================== AFFILIATE LINKS CRUD ====================
    
    def add_affiliate_link(self, website_id: int, anchor_text: str, url: str, 
                          category: str = None, priority: int = 0, 
                          link_type: str = 'direct', notes: str = None) -> Dict:
        """
        Voeg een nieuwe affiliate link toe
        
        Args:
            website_id: ID van de website
            anchor_text: Anchor text voor de link
            url: Affiliate URL
            category: Categorie (bijv. 'hotels', 'tours', 'products')
            priority: Prioriteit (hoger = vaker gebruikt)
            link_type: Type link ('direct', 'feed', 'api')
            notes: Notities
            
        Returns:
            Dict met success status en link_id
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO website_affiliate_links 
                (website_id, anchor_text, url, category, priority, link_type, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (website_id, anchor_text, url, category, priority, link_type, notes))
            
            link_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'link_id': link_id,
                'message': 'Affiliate link succesvol toegevoegd'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_affiliate_links(self, website_id: int, active_only: bool = True) -> List[Dict]:
        """
        Haal alle affiliate links op voor een website
        
        Args:
            website_id: ID van de website
            active_only: Alleen actieve links ophalen
            
        Returns:
            Lijst van affiliate links
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = '''
                SELECT * FROM website_affiliate_links 
                WHERE website_id = ?
            '''
            params = [website_id]
            
            if active_only:
                query += ' AND is_active = 1'
            
            query += ' ORDER BY priority DESC, created_at DESC'
            
            cursor.execute(query, params)
            links = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return links
        except Exception as e:
            print(f"Error getting affiliate links: {e}")
            return []
    
    def update_affiliate_link(self, link_id: int, **kwargs) -> Dict:
        """
        Update een affiliate link
        
        Args:
            link_id: ID van de link
            **kwargs: Velden om te updaten
            
        Returns:
            Dict met success status
        """
        try:
            allowed_fields = ['anchor_text', 'url', 'category', 'priority', 
                            'link_type', 'notes', 'is_active']
            
            updates = []
            values = []
            
            for field, value in kwargs.items():
                if field in allowed_fields:
                    updates.append(f"{field} = ?")
                    values.append(value)
            
            if not updates:
                return {'success': False, 'error': 'Geen geldige velden om te updaten'}
            
            updates.append("updated_at = CURRENT_TIMESTAMP")
            values.append(link_id)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = f"UPDATE website_affiliate_links SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, values)
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'message': 'Affiliate link succesvol geüpdatet'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_affiliate_link(self, link_id: int) -> Dict:
        """
        Verwijder een affiliate link
        
        Args:
            link_id: ID van de link
            
        Returns:
            Dict met success status
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM website_affiliate_links WHERE id = ?', (link_id,))
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'message': 'Affiliate link succesvol verwijderd'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    # ==================== AFFILIATE FEEDS CRUD ====================
    
    def add_affiliate_feed(self, website_id: int, feed_name: str, feed_url: str,
                          feed_type: str = 'xml', update_frequency: str = 'daily',
                          notes: str = None) -> Dict:
        """
        Voeg een nieuwe affiliate feed toe
        
        Args:
            website_id: ID van de website
            feed_name: Naam van de feed
            feed_url: URL van de feed
            feed_type: Type feed ('xml', 'json', 'csv')
            update_frequency: Update frequentie ('hourly', 'daily', 'weekly')
            notes: Notities
            
        Returns:
            Dict met success status en feed_id
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO website_affiliate_feeds 
                (website_id, feed_name, feed_url, feed_type, update_frequency, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (website_id, feed_name, feed_url, feed_type, update_frequency, notes))
            
            feed_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            # Probeer de feed direct te importeren
            import_result = self.import_feed_products(feed_id)
            
            return {
                'success': True,
                'feed_id': feed_id,
                'message': 'Affiliate feed succesvol toegevoegd',
                'import_result': import_result
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_affiliate_feeds(self, website_id: int, active_only: bool = True) -> List[Dict]:
        """
        Haal alle affiliate feeds op voor een website
        
        Args:
            website_id: ID van de website
            active_only: Alleen actieve feeds ophalen
            
        Returns:
            Lijst van affiliate feeds
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = '''
                SELECT * FROM website_affiliate_feeds 
                WHERE website_id = ?
            '''
            params = [website_id]
            
            if active_only:
                query += ' AND is_active = 1'
            
            query += ' ORDER BY created_at DESC'
            
            cursor.execute(query, params)
            feeds = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return feeds
        except Exception as e:
            print(f"Error getting affiliate feeds: {e}")
            return []
    
    def update_affiliate_feed(self, feed_id: int, **kwargs) -> Dict:
        """
        Update een affiliate feed
        
        Args:
            feed_id: ID van de feed
            **kwargs: Velden om te updaten
            
        Returns:
            Dict met success status
        """
        try:
            allowed_fields = ['feed_name', 'feed_url', 'feed_type', 
                            'update_frequency', 'notes', 'is_active']
            
            updates = []
            values = []
            
            for field, value in kwargs.items():
                if field in allowed_fields:
                    updates.append(f"{field} = ?")
                    values.append(value)
            
            if not updates:
                return {'success': False, 'error': 'Geen geldige velden om te updaten'}
            
            updates.append("updated_at = CURRENT_TIMESTAMP")
            values.append(feed_id)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = f"UPDATE website_affiliate_feeds SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, values)
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'message': 'Affiliate feed succesvol geüpdatet'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_affiliate_feed(self, feed_id: int) -> Dict:
        """
        Verwijder een affiliate feed en alle bijbehorende producten
        
        Args:
            feed_id: ID van de feed
            
        Returns:
            Dict met success status
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Verwijder eerst alle producten
            cursor.execute('DELETE FROM feed_products WHERE feed_id = ?', (feed_id,))
            
            # Verwijder de feed
            cursor.execute('DELETE FROM website_affiliate_feeds WHERE id = ?', (feed_id,))
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'message': 'Affiliate feed succesvol verwijderd'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    # ==================== FEED IMPORT ====================
    
    def import_feed_products(self, feed_id: int) -> Dict:
        """
        Importeer producten uit een affiliate feed
        
        Args:
            feed_id: ID van de feed
            
        Returns:
            Dict met import resultaten
        """
        try:
            # Haal feed info op
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM website_affiliate_feeds WHERE id = ?', (feed_id,))
            feed = cursor.fetchone()
            
            if not feed:
                return {'success': False, 'error': 'Feed niet gevonden'}
            
            feed = dict(feed)
            
            # Download feed
            response = requests.get(feed['feed_url'], timeout=30)
            response.raise_for_status()
            
            # Parse feed op basis van type
            products = []
            
            if feed['feed_type'] == 'xml':
                products = self._parse_xml_feed(response.content)
            elif feed['feed_type'] == 'json':
                products = self._parse_json_feed(response.json())
            elif feed['feed_type'] == 'csv':
                products = self._parse_csv_feed(response.text)
            
            # Verwijder oude producten
            cursor.execute('DELETE FROM feed_products WHERE feed_id = ?', (feed_id,))
            
            # Voeg nieuwe producten toe
            for product in products:
                cursor.execute('''
                    INSERT INTO feed_products 
                    (feed_id, product_id, product_name, product_url, product_price, 
                     product_category, product_image, product_description)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    feed_id,
                    product.get('id'),
                    product.get('name'),
                    product.get('url'),
                    product.get('price'),
                    product.get('category'),
                    product.get('image'),
                    product.get('description')
                ))
            
            # Update feed metadata
            cursor.execute('''
                UPDATE website_affiliate_feeds 
                SET last_updated = CURRENT_TIMESTAMP, product_count = ?
                WHERE id = ?
            ''', (len(products), feed_id))
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'products_imported': len(products),
                'message': f'{len(products)} producten succesvol geïmporteerd'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _parse_xml_feed(self, xml_content: bytes) -> List[Dict]:
        """Parse XML product feed"""
        products = []
        
        try:
            root = ET.fromstring(xml_content)
            
            # Probeer verschillende XML structuren
            # Google Shopping Feed format
            for item in root.findall('.//{http://base.google.com/ns/1.0}item'):
                product = {
                    'id': self._get_xml_text(item, '{http://base.google.com/ns/1.0}id'),
                    'name': self._get_xml_text(item, '{http://base.google.com/ns/1.0}title'),
                    'url': self._get_xml_text(item, '{http://base.google.com/ns/1.0}link'),
                    'price': self._get_xml_text(item, '{http://base.google.com/ns/1.0}price'),
                    'category': self._get_xml_text(item, '{http://base.google.com/ns/1.0}product_type'),
                    'image': self._get_xml_text(item, '{http://base.google.com/ns/1.0}image_link'),
                    'description': self._get_xml_text(item, '{http://base.google.com/ns/1.0}description')
                }
                products.append(product)
            
            # Generic XML format
            if not products:
                for item in root.findall('.//item') or root.findall('.//product'):
                    product = {
                        'id': self._get_xml_text(item, 'id') or self._get_xml_text(item, 'product_id'),
                        'name': self._get_xml_text(item, 'title') or self._get_xml_text(item, 'name'),
                        'url': self._get_xml_text(item, 'link') or self._get_xml_text(item, 'url'),
                        'price': self._get_xml_text(item, 'price'),
                        'category': self._get_xml_text(item, 'category') or self._get_xml_text(item, 'product_type'),
                        'image': self._get_xml_text(item, 'image') or self._get_xml_text(item, 'image_link'),
                        'description': self._get_xml_text(item, 'description')
                    }
                    products.append(product)
            
        except Exception as e:
            print(f"Error parsing XML feed: {e}")
        
        return products
    
    def _get_xml_text(self, element, tag: str) -> Optional[str]:
        """Helper om XML text veilig op te halen"""
        child = element.find(tag)
        return child.text if child is not None else None
    
    def _parse_json_feed(self, json_data: Dict) -> List[Dict]:
        """Parse JSON product feed"""
        products = []
        
        try:
            # Probeer verschillende JSON structuren
            items = json_data.get('items', json_data.get('products', []))
            
            for item in items:
                product = {
                    'id': item.get('id') or item.get('product_id'),
                    'name': item.get('title') or item.get('name'),
                    'url': item.get('link') or item.get('url'),
                    'price': item.get('price'),
                    'category': item.get('category') or item.get('product_type'),
                    'image': item.get('image') or item.get('image_link'),
                    'description': item.get('description')
                }
                products.append(product)
                
        except Exception as e:
            print(f"Error parsing JSON feed: {e}")
        
        return products
    
    def _parse_csv_feed(self, csv_content: str) -> List[Dict]:
        """Parse CSV product feed"""
        products = []
        
        try:
            import csv
            from io import StringIO
            
            reader = csv.DictReader(StringIO(csv_content))
            
            for row in reader:
                product = {
                    'id': row.get('id') or row.get('product_id'),
                    'name': row.get('title') or row.get('name'),
                    'url': row.get('link') or row.get('url'),
                    'price': row.get('price'),
                    'category': row.get('category') or row.get('product_type'),
                    'image': row.get('image') or row.get('image_link'),
                    'description': row.get('description')
                }
                products.append(product)
                
        except Exception as e:
            print(f"Error parsing CSV feed: {e}")
        
        return products
    
    # ==================== LINK GENERATION ====================
    
    def get_relevant_links(self, website_id: int, topic: str, 
                          max_links: int = 5) -> List[Dict]:
        """
        Haal relevante affiliate links op voor een specifiek onderwerp
        
        Args:
            website_id: ID van de website
            topic: Blog onderwerp
            max_links: Maximum aantal links
            
        Returns:
            Lijst van relevante affiliate links
        """
        try:
            # Haal alle actieve links op
            all_links = self.get_affiliate_links(website_id, active_only=True)
            
            if not all_links:
                return []
            
            # Score links op basis van relevantie
            scored_links = []
            topic_lower = topic.lower()
            
            for link in all_links:
                score = link['priority']
                
                # Verhoog score als categorie matcht met onderwerp
                if link['category']:
                    category_lower = link['category'].lower()
                    if category_lower in topic_lower or topic_lower in category_lower:
                        score += 10
                
                # Verhoog score als anchor text relevant is
                anchor_lower = link['anchor_text'].lower()
                common_words = set(anchor_lower.split()) & set(topic_lower.split())
                score += len(common_words) * 2
                
                scored_links.append((score, link))
            
            # Sorteer op score en return top N
            scored_links.sort(reverse=True, key=lambda x: x[0])
            return [link for score, link in scored_links[:max_links]]
            
        except Exception as e:
            print(f"Error getting relevant links: {e}")
            return []
    
    def get_feed_products_by_category(self, website_id: int, category: str = None,
                                     limit: int = 10) -> List[Dict]:
        """
        Haal producten op uit feeds voor een website
        
        Args:
            website_id: ID van de website
            category: Filter op categorie (optioneel)
            limit: Maximum aantal producten
            
        Returns:
            Lijst van producten
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = '''
                SELECT fp.* FROM feed_products fp
                JOIN website_affiliate_feeds waf ON fp.feed_id = waf.id
                WHERE waf.website_id = ? AND waf.is_active = 1
            '''
            params = [website_id]
            
            if category:
                query += ' AND fp.product_category LIKE ?'
                params.append(f'%{category}%')
            
            query += ' ORDER BY fp.created_at DESC LIMIT ?'
            params.append(limit)
            
            cursor.execute(query, params)
            products = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return products
            
        except Exception as e:
            print(f"Error getting feed products: {e}")
            return []
