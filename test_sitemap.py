#!/usr/bin/env python3
"""
Test script for sitemap fetching functionality
"""

from backend_utils import fetch_sitemap_urls

# Test URLs - common WordPress sitemap formats
test_urls = [
    "https://yoast.com/sitemap_index.xml",  # Yoast SEO sitemap index
    "https://wordpress.org/news/wp-sitemap.xml",  # WordPress core sitemap
]

print("=" * 60)
print("SITEMAP FETCH TEST")
print("=" * 60)

for test_url in test_urls:
    print(f"\n🧪 Testing: {test_url}")
    print("-" * 60)
    
    urls = fetch_sitemap_urls(test_url, max_urls=10)
    
    if urls:
        print(f"✅ SUCCESS: Found {len(urls)} URLs")
        print("\nFirst 3 URLs:")
        for i, url_data in enumerate(urls[:3], 1):
            print(f"  {i}. {url_data['title']}")
            print(f"     {url_data['url']}")
    else:
        print("❌ FAILED: No URLs found")
    
    print("-" * 60)

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
