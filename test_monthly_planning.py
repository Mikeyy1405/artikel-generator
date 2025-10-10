#!/usr/bin/env python3
"""
Test the new monthly content planning function
"""
import os
import sys

# Set OpenAI API key for testing
os.environ['OPENAI_API_KEY'] = os.environ.get('OPENAI_API_KEY', '')

from deepagent_research import deepagent_monthly_content_plan

print("🧪 Testing monthly content planning function...")
print("=" * 60)

# Test with different posting frequencies
test_cases = [
    {
        'domain': 'https://writgo.nl',
        'niche': 'SEO en online marketing',
        'country': 'Nederland',
        'language': 'Dutch',
        'description': 'Website over SEO, affiliate marketing, online geld verdienen en AI',
        'posting_frequency': '2x per week'
    },
    {
        'domain': 'https://example.com',
        'niche': 'Yoga en wellness',
        'country': 'Nederland',
        'language': 'Dutch',
        'description': 'Yoga oefeningen voor beginners',
        'posting_frequency': 'weekly'
    }
]

for i, test_case in enumerate(test_cases, 1):
    print(f"\n📝 Test Case {i}: {test_case['niche']} ({test_case['posting_frequency']})")
    print("-" * 60)
    
    result = deepagent_monthly_content_plan(**test_case)
    
    if result and result.get('success'):
        print(f"✅ SUCCESS!")
        print(f"   Domain: {result['domain']}")
        print(f"   Frequency: {result['posting_frequency']}")
        print(f"   Number of articles: {result['num_articles']}")
        print(f"\n📋 Content Plan Preview (first 500 chars):")
        print("-" * 60)
        content_preview = result['content_plan'][:500] if result['content_plan'] else 'No content'
        print(content_preview)
        print("...")
    else:
        print(f"❌ FAILED!")
        error = result.get('error', 'Unknown error') if result else 'No result returned'
        print(f"   Error: {error}")
    
    print("=" * 60)

print("\n✅ Testing completed!")
