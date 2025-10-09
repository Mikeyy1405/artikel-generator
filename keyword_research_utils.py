
"""
Keyword Research Utilities
Intelligent competitor analysis and content gap detection
"""

import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from collections import Counter
import json

def analyze_site_content(website_context, website_links):
    """
    Analyze current site content to understand topics and keywords
    
    Args:
        website_context: Dict with site information from localStorage
        website_links: List of scraped links from the site
    
    Returns:
        dict: Site analysis with main_topic, subtopics, keywords
    """
    try:
        # Extract main topic from site name/URL
        site_url = website_context.get('site_url', '')
        site_name = website_context.get('site_name', '')
        
        # Parse domain for topic hints
        parsed = urlparse(site_url)
        domain_parts = parsed.netloc.replace('www.', '').split('.')
        domain_name = domain_parts[0] if domain_parts else ''
        
        # Analyze link texts to find common themes
        all_text = []
        if website_links:
            for link in website_links:
                if isinstance(link, dict):
                    anchor = link.get('anchor_text', '')
                    url = link.get('url', '')
                    all_text.append(anchor)
                    # Extract keywords from URL path
                    path_parts = urlparse(url).path.split('/')
                    all_text.extend([p.replace('-', ' ').replace('_', ' ') for p in path_parts if p])
        
        # Extract keywords (simple frequency analysis)
        words = []
        for text in all_text:
            if text:
                # Clean and split
                clean_text = re.sub(r'[^\w\s]', ' ', text.lower())
                words.extend([w for w in clean_text.split() if len(w) > 3])
        
        # Count word frequency
        word_freq = Counter(words)
        top_keywords = [word for word, count in word_freq.most_common(20)]
        
        # Determine main topic (use site name or domain)
        main_topic = site_name or domain_name.replace('-', ' ').replace('_', ' ').title()
        
        # Extract subtopics from most common keywords
        subtopics = top_keywords[:10]
        
        return {
            'main_topic': main_topic,
            'subtopics': subtopics,
            'keywords': top_keywords,
            'domain': parsed.netloc
        }
        
    except Exception as e:
        print(f"❌ Error analyzing site content: {e}")
        return {
            'main_topic': 'Unknown',
            'subtopics': [],
            'keywords': [],
            'domain': ''
        }


def find_competitors(keyword, main_topic, num_competitors=5):
    """
    Find competitor websites using web search
    
    Args:
        keyword: Main keyword to search for
        main_topic: Main topic of the site
        num_competitors: Number of competitors to find
    
    Returns:
        list: List of competitor URLs
    """
    try:
        # This is a placeholder - in production, you would use:
        # 1. Google Custom Search API
        # 2. Bing Search API
        # 3. Or the web_search tool from the agent
        
        # For now, return common competitor patterns
        # In real implementation, this would call the web_search tool
        
        competitors = []
        
        # Search queries to find competitors
        search_queries = [
            f"best {main_topic} websites",
            f"top {keyword} blogs",
            f"{keyword} information sites",
            f"popular {main_topic} resources"
        ]
        
        # This would be replaced with actual web search API calls
        # For now, return empty list - will be populated by the agent's web_search tool
        
        return competitors
        
    except Exception as e:
        print(f"❌ Error finding competitors: {e}")
        return []


def scrape_competitor(competitor_url):
    """
    Scrape competitor website content
    
    Args:
        competitor_url: URL of competitor site
    
    Returns:
        str: Scraped text content
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(competitor_url, timeout=15, headers=headers)
        if response.status_code != 200:
            return ""
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Get text
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text[:10000]  # Limit to first 10k characters
        
    except Exception as e:
        print(f"❌ Error scraping competitor {competitor_url}: {e}")
        return ""


def extract_topics(content):
    """
    Extract main topics from content using keyword frequency
    
    Args:
        content: Text content
    
    Returns:
        list: List of main topics
    """
    try:
        if not content:
            return []
        
        # Clean text
        clean_text = re.sub(r'[^\w\s]', ' ', content.lower())
        words = [w for w in clean_text.split() if len(w) > 4]
        
        # Count frequency
        word_freq = Counter(words)
        
        # Get top topics (excluding common words)
        stop_words = {'about', 'there', 'their', 'which', 'would', 'could', 'should', 
                     'these', 'those', 'where', 'when', 'what', 'have', 'with', 'from'}
        
        topics = [word for word, count in word_freq.most_common(30) 
                 if word not in stop_words and count > 2]
        
        return topics[:15]
        
    except Exception as e:
        print(f"❌ Error extracting topics: {e}")
        return []


def extract_keywords(content):
    """
    Extract keywords from content (2-3 word phrases)
    
    Args:
        content: Text content
    
    Returns:
        list: List of keyword phrases
    """
    try:
        if not content:
            return []
        
        # Clean text
        clean_text = re.sub(r'[^\w\s]', ' ', content.lower())
        words = clean_text.split()
        
        # Extract 2-3 word phrases
        phrases = []
        for i in range(len(words) - 2):
            phrase2 = f"{words[i]} {words[i+1]}"
            phrase3 = f"{words[i]} {words[i+1]} {words[i+2]}"
            
            # Filter out phrases with very short words
            if all(len(w) > 2 for w in phrase2.split()):
                phrases.append(phrase2)
            if all(len(w) > 2 for w in phrase3.split()):
                phrases.append(phrase3)
        
        # Count frequency
        phrase_freq = Counter(phrases)
        
        # Get top keywords
        keywords = [phrase for phrase, count in phrase_freq.most_common(20) if count > 1]
        
        return keywords[:15]
        
    except Exception as e:
        print(f"❌ Error extracting keywords: {e}")
        return []


def identify_gaps(site_topics, competitor_analysis):
    """
    Identify content gaps between your site and competitors
    
    Args:
        site_topics: Dict with your site's topics and keywords
        competitor_analysis: List of competitor analysis dicts
    
    Returns:
        list: List of content gaps (topics/keywords competitors have that you don't)
    """
    try:
        # Get your site's topics and keywords
        your_topics = set(site_topics.get('subtopics', []))
        your_keywords = set(site_topics.get('keywords', []))
        
        # Collect all competitor topics and keywords
        competitor_topics = set()
        competitor_keywords = set()
        
        for comp in competitor_analysis:
            competitor_topics.update(comp.get('topics', []))
            competitor_keywords.update(comp.get('keywords', []))
        
        # Find gaps (what they have that you don't)
        topic_gaps = list(competitor_topics - your_topics)
        keyword_gaps = list(competitor_keywords - your_keywords)
        
        # Combine and prioritize
        all_gaps = []
        
        # Add topic gaps with high priority
        for topic in topic_gaps[:10]:
            all_gaps.append({
                'type': 'topic',
                'value': topic,
                'priority': 'high'
            })
        
        # Add keyword gaps with medium priority
        for keyword in keyword_gaps[:15]:
            all_gaps.append({
                'type': 'keyword',
                'value': keyword,
                'priority': 'medium'
            })
        
        return all_gaps
        
    except Exception as e:
        print(f"❌ Error identifying gaps: {e}")
        return []


def generate_keywords_from_gaps(content_gaps, base_keyword):
    """
    Generate keyword suggestions based on content gaps
    
    Args:
        content_gaps: List of content gap dicts
        base_keyword: Base keyword from user input
    
    Returns:
        list: List of keyword suggestions with metadata
    """
    try:
        suggestions = []
        
        for gap in content_gaps:
            gap_value = gap.get('value', '')
            gap_type = gap.get('type', 'keyword')
            priority = gap.get('priority', 'medium')
            
            # Generate keyword variations
            if gap_type == 'topic':
                # Topic-based keywords
                variations = [
                    f"{base_keyword} {gap_value}",
                    f"{gap_value} {base_keyword}",
                    f"beste {gap_value} voor {base_keyword}",
                    f"{gap_value} tips",
                    f"hoe {gap_value}"
                ]
            else:
                # Keyword-based suggestions
                variations = [
                    gap_value,
                    f"{base_keyword} {gap_value}",
                    f"{gap_value} gids"
                ]
            
            for variation in variations:
                suggestions.append({
                    'keyword': variation,
                    'priority': priority,
                    'source': f"Gap: {gap_value}",
                    'type': gap_type,
                    'search_volume': 'Unknown',  # Would be populated by keyword tool API
                    'difficulty': 'Unknown'  # Would be populated by SEO tool API
                })
        
        # Remove duplicates
        seen = set()
        unique_suggestions = []
        for sugg in suggestions:
            if sugg['keyword'] not in seen:
                seen.add(sugg['keyword'])
                unique_suggestions.append(sugg)
        
        return unique_suggestions[:30]  # Return top 30 suggestions
        
    except Exception as e:
        print(f"❌ Error generating keywords from gaps: {e}")
        return []
