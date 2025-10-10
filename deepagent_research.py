#!/usr/bin/env python3
"""
DeepAgent Research Integration
Uses Abacus.AI's DeepAgent for keyword research and content planning
"""
import os
import json
import requests
import time
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


def deepagent_monthly_content_plan(domain, niche, country, language, description="", posting_frequency="2x per week"):
    """
    Generate a MONTHLY content plan based on posting frequency
    This is faster and more practical than generating 150+ keywords
    
    Args:
        domain: Website domain
        niche: Business niche/industry
        country: Target country
        language: Content language
        description: Optional website description
        posting_frequency: Posting frequency ('daily', '2x per week', '3x per week', 'weekly')
    
    Returns:
        dict: Monthly content plan with article topics
    """
    import time
    from datetime import datetime
    
    start_time = time.time()
    print(f"📅 [DEEPAGENT] Starting monthly content plan for {domain} at {datetime.now().strftime('%H:%M:%S')}")
    
    # Calculate number of articles based on posting frequency
    frequency_map = {
        'daily': 30,
        '2x per week': 8,
        '3x per week': 12,
        'weekly': 4,
        'dagelijks': 30,
        '2x per week': 8,
        '3x per week': 12,
        'wekelijks': 4
    }
    
    num_articles = frequency_map.get(posting_frequency.lower(), 8)  # Default to 2x per week
    
    print(f"📊 [DEEPAGENT] Frequency: {posting_frequency} → {num_articles} articles/month")
    
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
    
    # Build focused prompt for monthly content planning
    # Optimized shorter prompt for faster API response
    desc_line = f"\n- Description: {description}" if description else ""
    prompt = f"""
Create monthly content plan for {domain}

Website: {niche} | {country} | {language}{desc_line}
Posting: {posting_frequency} = {num_articles} articles/month

Generate {num_articles} SEO-optimized article ideas. For each provide:

1. Number & Title (in {language}, engaging, SEO-friendly)
2. Primary Keyword + 2-3 Secondary Keywords (in {language})
3. Content Type (Guide/Listicle/How-to/Comparison)
4. Search Intent (Informational/Commercial/Transactional)
5. Word Count estimate
6. 3-5 section outline
7. Priority (High/Medium/Low)

Requirements:
- All content in {language} for {country} market
- Mix different content types and intents
- Build topical authority
- Clear, structured format
"""
    
    try:
        print(f"🤖 [DEEPAGENT] Calling OpenAI API for monthly content plan...")
        
        if not client:
            error_msg = "OpenAI API key not configured - please set OPENAI_API_KEY environment variable"
            print(f"❌ [DEEPAGENT] {error_msg}")
            raise Exception(error_msg)
        
        # Retry logic with exponential backoff
        max_retries = 3
        retry_delay = 2  # seconds
        
        for attempt in range(max_retries):
            try:
                print(f"🔄 [DEEPAGENT] API call attempt {attempt + 1}/{max_retries}...")
                
                response = client.chat.completions.create(
                    model="gpt-4o-mini",  # Using mini for faster response
                    messages=[
                        {
                            "role": "system",
                            "content": f"You are an expert content strategist specializing in {language} content for {country}. Create practical, actionable monthly content plans."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.5,
                    max_tokens=2000,  # Reduced for faster response
                    timeout=90  # 90 second timeout per API call
                )
                
                content_plan_text = response.choices[0].message.content
                elapsed_time = time.time() - start_time
                
                print(f"✅ [DEEPAGENT] Monthly content plan completed in {elapsed_time:.2f} seconds")
                
                return {
                    'success': True,
                    'content_plan': content_plan_text,
                    'num_articles': num_articles,
                    'posting_frequency': posting_frequency,
                    'domain': domain,
                    'niche': niche,
                    'country': country,
                    'language': language,
                    'generated_at': datetime.now().isoformat(),
                    'generation_time': f"{elapsed_time:.2f}s"
                }
                
            except Exception as api_error:
                print(f"⚠️ [DEEPAGENT] Attempt {attempt + 1} failed: {str(api_error)}")
                
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                    print(f"⏳ [DEEPAGENT] Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    raise  # Re-raise the last exception if all retries failed
        
    except Exception as e:
        elapsed_time = time.time() - start_time
        error_details = f"Error: {str(e)} | Type: {type(e).__name__} | Time: {elapsed_time:.2f}s"
        print(f"❌ [DEEPAGENT] Monthly content planning failed after {elapsed_time:.2f}s")
        print(f"❌ [DEEPAGENT] {error_details}")
        
        return {
            'success': False,
            'error': str(e),
            'error_details': error_details,
            'content_plan': None,
            'generation_time': f"{elapsed_time:.2f}s"
        }


def deepagent_content_planning(keywords_data, domain, niche, num_articles=10, posting_schedule="weekly"):
    """
    Use DeepAgent (or OpenAI) to create content plan from keyword research
    (LEGACY - kept for backward compatibility)
    
    Args:
        keywords_data: Keyword research results
        domain: Website domain
        niche: Business niche
        num_articles: Number of articles to plan
        posting_schedule: Posting frequency
    
    Returns:
        dict: Content plan with article topics and structure
    """
    start_time = datetime.now()
    print(f"📋 [DEEPAGENT] Starting content planning for {domain} at {start_time.strftime('%H:%M:%S')}")
    
    # Truncate keywords_data if too long to prevent timeout
    max_keywords_length = 2000  # Reduced from 3000 for faster processing
    if len(keywords_data) > max_keywords_length:
        print(f"⚠️ [DEEPAGENT] Truncating keywords data from {len(keywords_data)} to {max_keywords_length} characters")
        keywords_data = keywords_data[:max_keywords_length] + "..."
    
    # Ultra-simplified prompt for maximum speed
    prompt = f"""
{num_articles} article plan for {domain} ({niche}, {posting_schedule})

Keywords: {keywords_data}

For each article provide:
1. Title (SEO)
2. Keyword
3. Type
4. 3-section outline

Format: Numbered list (1., 2., 3...)
Be extremely concise.
"""
    
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(1, max_retries + 1):
        try:
            print(f"🤖 [DEEPAGENT] Content planning API call {attempt}/{max_retries}...")
            print(f"📊 [DEEPAGENT] Prompt length: {len(prompt)} chars")
            
            if not client:
                error_msg = "OpenAI API key not configured"
                print(f"❌ [DEEPAGENT] {error_msg}")
                raise Exception(error_msg)
            
            # Use faster model and increased timeout
            response = client.chat.completions.create(
                model="gpt-4o-mini",  # Faster model
                messages=[
                    {
                        "role": "system",
                        "content": "Expert content strategist. Ultra-concise plans."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=1000,  # Further reduced for speed
                timeout=120  # Increased from 20 to 120 seconds
            )
            
            content_plan_text = response.choices[0].message.content
            
            elapsed_time = (datetime.now() - start_time).total_seconds()
            print(f"✅ [DEEPAGENT] Content planning completed in {elapsed_time:.2f} seconds")
            print(f"📊 [DEEPAGENT] Response length: {len(content_plan_text)} chars")
            
            return {
                'success': True,
                'content_plan': content_plan_text,
                'num_articles': num_articles,
                'domain': domain,
                'niche': niche,
                'posting_schedule': posting_schedule,
                'generated_at': datetime.now().isoformat(),
                'generation_time': elapsed_time
            }
            
        except Exception as e:
            elapsed_time = (datetime.now() - start_time).total_seconds()
            error_type = type(e).__name__
            print(f"❌ [DEEPAGENT] Attempt {attempt} failed after {elapsed_time:.2f}s: {error_type}: {str(e)}")
            
            if attempt < max_retries:
                wait_time = retry_delay * (2 ** (attempt - 1))  # Exponential backoff
                print(f"🔄 [DEEPAGENT] Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print(f"❌ [DEEPAGENT] All {max_retries} attempts failed after {elapsed_time:.2f}s total")
                return {
                    'success': False,
                    'error': str(e),
                    'error_type': error_type,
                    'content_plan': None,
                    'generation_time': elapsed_time
                }
    
    # Fallback return (should never reach here)
    return {
        'success': False,
        'error': 'Maximum retries exceeded',
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
