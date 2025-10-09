
"""
Backend utility functions for WritgoAI
Includes sitemap detection, internal links extraction, affiliate link detection
"""

import requests
import re
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

def find_sitemap(base_url):
    """
    Automatically detect sitemap.xml or sitemap_index.xml from a website
    
    Args:
        base_url: Base URL of the website (e.g., https://example.com)
    
    Returns:
        dict: {"success": bool, "sitemap_url": str, "type": str, "error": str}
    """
    try:
        # Normalize URL
        if not base_url.startswith(('http://', 'https://')):
            base_url = 'https://' + base_url
        
        parsed = urlparse(base_url)
        base_domain = f"{parsed.scheme}://{parsed.netloc}"
        
        # Common sitemap locations to check
        sitemap_paths = [
            '/sitemap.xml',
            '/sitemap_index.xml',
            '/sitemap-index.xml',
            '/sitemap1.xml',
            '/wp-sitemap.xml',
            '/sitemap.php'
        ]
        
        # First, try robots.txt
        try:
            robots_url = urljoin(base_domain, '/robots.txt')
            response = requests.get(robots_url, timeout=10)
            if response.status_code == 200:
                # Look for Sitemap: directive in robots.txt
                for line in response.text.split('\n'):
                    if line.lower().startswith('sitemap:'):
                        sitemap_url = line.split(':', 1)[1].strip()
                        # Verify the sitemap exists
                        verify_response = requests.head(sitemap_url, timeout=10)
                        if verify_response.status_code == 200:
                            sitemap_type = 'sitemap_index' if 'index' in sitemap_url.lower() else 'sitemap'
                            return {
                                "success": True,
                                "sitemap_url": sitemap_url,
                                "type": sitemap_type,
                                "source": "robots.txt"
                            }
        except:
            pass
        
        # Try common sitemap paths
        for path in sitemap_paths:
            sitemap_url = urljoin(base_domain, path)
            try:
                response = requests.head(sitemap_url, timeout=10)
                if response.status_code == 200:
                    sitemap_type = 'sitemap_index' if 'index' in path else 'sitemap'
                    return {
                        "success": True,
                        "sitemap_url": sitemap_url,
                        "type": sitemap_type,
                        "source": "common_path"
                    }
            except:
                continue
        
        return {
            "success": False,
            "error": "No sitemap found at common locations"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error detecting sitemap: {str(e)}"
        }


def extract_internal_links(base_url, max_links=50):
    """
    Extract internal links from a website's homepage
    
    Args:
        base_url: Base URL of the website
        max_links: Maximum number of links to extract
    
    Returns:
        dict: {"success": bool, "links": list, "error": str}
    """
    try:
        # Normalize URL
        if not base_url.startswith(('http://', 'https://')):
            base_url = 'https://' + base_url
        
        parsed_base = urlparse(base_url)
        base_domain = parsed_base.netloc
        
        # Fetch the homepage
        response = requests.get(base_url, timeout=15, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        if response.status_code != 200:
            return {
                "success": False,
                "error": f"Failed to fetch page: HTTP {response.status_code}"
            }
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all anchor tags
        all_links = soup.find_all('a', href=True)
        
        internal_links = []
        seen_urls = set()
        
        for link in all_links:
            if len(internal_links) >= max_links:
                break
            
            href = link.get('href', '').strip()
            if not href or href.startswith(('#', 'javascript:', 'mailto:', 'tel:')):
                continue
            
            # Convert relative URLs to absolute
            absolute_url = urljoin(base_url, href)
            parsed_url = urlparse(absolute_url)
            
            # Check if it's an internal link (same domain)
            if parsed_url.netloc == base_domain or not parsed_url.netloc:
                # Clean URL (remove fragments)
                clean_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
                if parsed_url.query:
                    clean_url += f"?{parsed_url.query}"
                
                # Avoid duplicates
                if clean_url not in seen_urls and clean_url != base_url:
                    seen_urls.add(clean_url)
                    
                    # Get anchor text
                    anchor_text = link.get_text(strip=True)
                    if not anchor_text:
                        anchor_text = "Link"
                    
                    internal_links.append({
                        "url": clean_url,
                        "anchor_text": anchor_text[:100]  # Limit length
                    })
        
        return {
            "success": True,
            "links": internal_links,
            "count": len(internal_links)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error extracting internal links: {str(e)}"
        }


def detect_affiliate_links(html_content):
    """
    Detect affiliate links in HTML content
    
    Args:
        html_content: HTML content as string
    
    Returns:
        dict: {"success": bool, "links": list, "error": str}
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        all_links = soup.find_all('a', href=True)
        
        affiliate_links = []
        
        # Common affiliate link patterns
        affiliate_patterns = [
            # Amazon
            r'amazon\.[a-z.]+/.*[?&]tag=',
            r'amzn\.to/',
            # ClickBank
            r'hop\.clickbank\.net',
            r'[?&]affiliate=',
            r'[?&]tid=',
            # ShareASale
            r'shareasale\.com',
            # CJ Affiliate
            r'anrdoezrs\.net',
            r'dpbolvw\.net',
            r'jdoqocy\.com',
            # Awin
            r'awin1\.com',
            # Rakuten
            r'rakuten\.[a-z.]+',
            # Impact
            r'impact\.com',
            # General patterns
            r'[?&]ref=',
            r'[?&]referral=',
            r'[?&]aff_id=',
            r'[?&]affid=',
            r'[?&]partner=',
            r'/ref/',
            r'/aff/',
        ]
        
        seen_urls = set()
        
        for link in all_links:
            href = link.get('href', '').strip()
            if not href:
                continue
            
            # Check against patterns
            is_affiliate = False
            for pattern in affiliate_patterns:
                if re.search(pattern, href, re.IGNORECASE):
                    is_affiliate = True
                    break
            
            if is_affiliate and href not in seen_urls:
                seen_urls.add(href)
                
                anchor_text = link.get_text(strip=True)
                if not anchor_text:
                    anchor_text = "Affiliate Link"
                
                affiliate_links.append({
                    "url": href,
                    "anchor_text": anchor_text[:100]
                })
        
        return {
            "success": True,
            "links": affiliate_links,
            "count": len(affiliate_links)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error detecting affiliate links: {str(e)}"
        }


def fetch_sitemap_urls(sitemap_url, max_urls=100):
    """
    Fetch URLs from a sitemap.xml or sitemap_index.xml
    
    Args:
        sitemap_url: URL of the sitemap
        max_urls: Maximum number of URLs to fetch
    
    Returns:
        list: List of URL dictionaries with 'url' and 'title' keys, or empty list on error
    """
    try:
        print(f"🔍 Fetching sitemap: {sitemap_url}")
        response = requests.get(sitemap_url, timeout=15, headers={
            'User-Agent': 'Mozilla/5.0 (compatible; WritgoAI/1.0)'
        })
        
        if response.status_code != 200:
            print(f"❌ Failed to fetch sitemap: HTTP {response.status_code}")
            return []
        
        # Parse XML with BeautifulSoup for better handling
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.content, 'xml')
        
        urls = []
        
        # Check if it's a sitemap index
        sitemaps = soup.find_all('sitemap')
        if sitemaps:
            print(f"📑 Found sitemap index with {len(sitemaps)} sub-sitemaps")
            # It's a sitemap index, fetch all sub-sitemaps
            for sitemap in sitemaps[:5]:  # Limit to first 5 sub-sitemaps
                loc = sitemap.find('loc')
                if loc and loc.text:
                    sub_sitemap_url = loc.text
                    try:
                        print(f"  📄 Fetching sub-sitemap: {sub_sitemap_url}")
                        sub_response = requests.get(sub_sitemap_url, timeout=15, headers={
                            'User-Agent': 'Mozilla/5.0 (compatible; WritgoAI/1.0)'
                        })
                        if sub_response.status_code == 200:
                            sub_soup = BeautifulSoup(sub_response.content, 'xml')
                            sub_locs = sub_soup.find_all('loc')
                            for loc_elem in sub_locs:
                                if loc_elem.text and len(urls) < max_urls:
                                    # Extract title from URL
                                    from urllib.parse import urlparse
                                    path = urlparse(loc_elem.text).path
                                    title = path.strip('/').split('/')[-1].replace('-', ' ').title() if path.strip('/') else loc_elem.text
                                    urls.append({
                                        'url': loc_elem.text,
                                        'title': title
                                    })
                            print(f"    ✅ Found {len(sub_locs)} URLs")
                    except Exception as e:
                        print(f"    ⚠️  Error fetching sub-sitemap: {str(e)}")
                        continue
        else:
            # It's a regular sitemap
            locs = soup.find_all('loc')
            print(f"📄 Found regular sitemap with {len(locs)} URLs")
            for loc_elem in locs[:max_urls]:
                if loc_elem.text:
                    # Extract title from URL
                    from urllib.parse import urlparse
                    path = urlparse(loc_elem.text).path
                    title = path.strip('/').split('/')[-1].replace('-', ' ').title() if path.strip('/') else loc_elem.text
                    urls.append({
                        'url': loc_elem.text,
                        'title': title
                    })
        
        print(f"✅ Successfully fetched {len(urls)} URLs from sitemap")
        return urls
        
    except Exception as e:
        print(f"❌ Error fetching sitemap URLs: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return []
