#!/usr/bin/env python3
"""
Daily Sitemap Refresh Script
Refreshes all saved sitemaps automatically
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sitemap_manager import refresh_all_sitemaps
from datetime import datetime

def main():
    print(f"\n{'='*60}")
    print(f"🔄 Daily Sitemap Refresh - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    result = refresh_all_sitemaps()
    
    if result['success']:
        print(f"\n✅ Refresh completed successfully!")
        print(f"   Total refreshed: {result['total_refreshed']}")
        print(f"\n📊 Results:")
        for r in result['results']:
            status = '✅' if r['success'] else '❌'
            print(f"   {status} {r['website_url']}: {r['message']} ({r['total_count']} URLs)")
    else:
        print(f"\n❌ Refresh failed")
    
    print(f"\n{'='*60}\n")

if __name__ == '__main__':
    main()
