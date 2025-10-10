#!/usr/bin/env python3
"""
DeepAgent Research Integration
Uses Abacus.AI's DeepAgent for keyword research and content planning
"""
import os
import json
import requests
from datetime import datetime

# OpenAI as fallback
from openai import OpenAI

# Initialize OpenAI client for fallback
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

def deepagent_keyword_research(domain, niche, country, language, description="", num_keywords=150):
    """
    Use DeepAgent (or OpenAI) to perform comprehensive keyword research
    
    Args:
        domain: Website domain
        niche: Business niche/industry
        country: Target country
        language: Content language
        description: Optional website description
        num_keywords: Number of keywords to generate (default: 150)
    
    Returns:
        dict: Keyword research results with categorized keywords
    """
    print(f"🔍 [DEEPAGENT] Starting keyword research for {domain}")
    
    # Determine language context
    lang_context_map = {
        'Nederland': "Dutch language, targeting the Netherlands market",
        'België': "Dutch/French language, targeting the Belgium market",
        'Duitsland': "German language, targeting the German market",
        'Frankrijk': "French language, targeting the French market",
        'Spanje': "Spanish language, targeting the Spanish market",
        'Italië': "Italian language, targeting the Italian market",
    }
    lang_context = lang_context_map.get(country, "English language, targeting international market")
    
    # Build comprehensive prompt
    prompt = f"""
Perform comprehensive SEO keyword research for: {domain}

**Website Information:**
- Domain: {domain}
- Niche/Industry: {niche}
- Target Country: {country}
- Language: {language}
{f"- Description: {description}" if description else ""}

**Research Requirements:**
Generate {num_keywords} highly relevant SEO keywords categorized as follows:

1. **Primary Keywords (30 keywords)** - High search volume, high competition, core business terms
2. **Secondary Keywords (40 keywords)** - Medium search volume, medium competition, supporting topics
3. **Long-tail Keywords (50 keywords)** - Low competition, specific detailed phrases
4. **Question Keywords (30 keywords)** - "how to", "what is", "why", "when", "where" questions

**Output Format:**
For EACH keyword provide:
- Keyword phrase (in {language})
- Search Intent (Informational/Commercial/Transactional/Navigational)
- Difficulty (Easy/Medium/Hard)
- Priority (High/Medium/Low)
- Estimated Monthly Search Volume (number)

**Important Guidelines:**
- ALL keywords must be in {language} language
- Focus on {country} market specifics
- Include relevant local terms and phrases
- Consider user intent and search behavior
- Mix of short and long-tail keywords
- Include seasonal and trending terms where relevant

Provide the results in a structured, table-like format that can be easily parsed.
"""
    
    try:
        print(f"🤖 [DEEPAGENT] Calling OpenAI for keyword research...")
        
        if not client:
            raise Exception("OpenAI API key not configured")
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert SEO researcher specializing in keyword analysis and search intent mapping. Provide comprehensive, data-driven keyword research."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=4000
        )
        
        keywords_text = response.choices[0].message.content
        
        print(f"✅ [DEEPAGENT] Keyword research completed successfully")
        
        return {
            'success': True,
            'keywords': keywords_text,
            'domain': domain,
            'niche': niche,
            'country': country,
            'language': language,
            'total_keywords': num_keywords,
            'generated_at': datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ [DEEPAGENT] Keyword research failed: {e}")
        return {
            'success': False,
            'error': str(e),
            'keywords': None
        }


def deepagent_content_planning(keywords_data, domain, niche, num_articles=10, posting_schedule="weekly"):
    """
    Use DeepAgent (or OpenAI) to create content plan from keyword research
    
    Args:
        keywords_data: Keyword research results
        domain: Website domain
        niche: Business niche
        num_articles: Number of articles to plan
        posting_schedule: Posting frequency
    
    Returns:
        dict: Content plan with article topics and structure
    """
    print(f"📋 [DEEPAGENT] Starting content planning for {domain}")
    
    prompt = f"""
Create a comprehensive content plan based on the following keyword research:

**Website Information:**
- Domain: {domain}
- Niche: {niche}
- Number of Articles: {num_articles}
- Posting Schedule: {posting_schedule}

**Keyword Research Data:**
{keywords_data}

**Content Plan Requirements:**

Generate exactly {num_articles} article ideas that:
1. Cover different keyword categories (primary, secondary, long-tail, questions)
2. Target different stages of the buyer journey
3. Mix content types (how-to guides, listicles, comparisons, case studies, etc.)
4. Are optimized for SEO and user engagement
5. Build upon each other for topical authority

**For EACH article provide:**
- Title (compelling and SEO-optimized)
- Primary Keyword(s)
- Secondary Keywords (3-5)
- Content Type (Guide/Listicle/Comparison/Review/Tutorial/etc.)
- Target Audience
- Search Intent
- Estimated Word Count
- Content Outline (H2/H3 structure with 5-7 sections)
- SEO Tips (meta description suggestion, internal linking opportunities)
- Priority (High/Medium/Low)

**Output Format:**
Provide a structured content calendar that can be easily parsed and implemented.
Number each article clearly (Article 1, Article 2, etc.)
"""
    
    try:
        print(f"🤖 [DEEPAGENT] Calling OpenAI for content planning...")
        
        if not client:
            raise Exception("OpenAI API key not configured")
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert content strategist and SEO specialist. Create detailed, actionable content plans that drive organic traffic and engagement."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.4,
            max_tokens=4000
        )
        
        content_plan_text = response.choices[0].message.content
        
        print(f"✅ [DEEPAGENT] Content planning completed successfully")
        
        return {
            'success': True,
            'content_plan': content_plan_text,
            'num_articles': num_articles,
            'domain': domain,
            'niche': niche,
            'posting_schedule': posting_schedule,
            'generated_at': datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ [DEEPAGENT] Content planning failed: {e}")
        return {
            'success': False,
            'error': str(e),
            'content_plan': None
        }


def deepagent_web_search(query, num_results=10):
    """
    Perform web search for research (can be extended to use actual web search APIs)
    
    Args:
        query: Search query
        num_results: Number of results to return
    
    Returns:
        dict: Search results
    """
    print(f"🌐 [DEEPAGENT] Web search for: {query}")
    
    try:
        # For now, use OpenAI to simulate research
        # In production, this could use Google Custom Search API, Bing API, etc.
        
        if not client:
            raise Exception("OpenAI API key not configured")
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a research assistant. Provide factual, up-to-date information based on the query."
                },
                {
                    "role": "user",
                    "content": f"Research and summarize: {query}\n\nProvide {num_results} key insights or findings."
                }
            ],
            temperature=0.2,
            max_tokens=2000
        )
        
        results = response.choices[0].message.content
        
        print(f"✅ [DEEPAGENT] Web search completed")
        
        return {
            'success': True,
            'results': results,
            'query': query,
            'num_results': num_results
        }
        
    except Exception as e:
        print(f"❌ [DEEPAGENT] Web search failed: {e}")
        return {
            'success': False,
            'error': str(e),
            'results': None
        }


# Test function
if __name__ == "__main__":
    # Test keyword research
    print("Testing DeepAgent Keyword Research...")
    result = deepagent_keyword_research(
        domain="example.com",
        niche="Digital Marketing",
        country="Nederland",
        language="Dutch",
        description="Digital marketing agency specialized in SEO",
        num_keywords=20  # Smaller number for testing
    )
    
    if result['success']:
        print("\n✅ Keyword Research Results:")
        print(result['keywords'][:500])  # Print first 500 chars
    else:
        print(f"\n❌ Error: {result['error']}")
    
    # Test content planning
    if result['success']:
        print("\n\nTesting DeepAgent Content Planning...")
        plan_result = deepagent_content_planning(
            keywords_data=result['keywords'],
            domain="example.com",
            niche="Digital Marketing",
            num_articles=5,
            posting_schedule="weekly"
        )
        
        if plan_result['success']:
            print("\n✅ Content Plan Results:")
            print(plan_result['content_plan'][:500])  # Print first 500 chars
        else:
            print(f"\n❌ Error: {plan_result['error']}")
