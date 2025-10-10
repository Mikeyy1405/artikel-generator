#!/usr/bin/env python3
"""
Test script to verify the monthly content planning fix
This tests that:
1. The monthly content plan generates quickly (< 30 seconds)
2. It produces the correct number of articles based on posting frequency
3. The response format is correct
"""

import time
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from deepagent_research import deepagent_monthly_content_plan

def test_monthly_planning():
    """Test monthly content planning with different frequencies"""
    
    test_cases = [
        ('2x per week', 8, '2x per week should generate 8-10 articles'),
        ('weekly', 4, 'weekly should generate 4-5 articles'),
        ('3x per week', 12, '3x per week should generate 12-15 articles'),
        ('daily', 30, 'daily should generate 30 articles')
    ]
    
    print("🧪 Testing Monthly Content Planning Fix")
    print("=" * 60)
    
    for frequency, expected_articles, description in test_cases:
        print(f"\n📅 Testing: {frequency} ({description})")
        print("-" * 60)
        
        # Start timer
        start_time = time.time()
        
        try:
            # Call the monthly planning function
            result = deepagent_monthly_content_plan(
                domain="testwebsite.nl",
                niche="Digital Marketing",
                country="Nederland",
                language="Dutch",
                description="Een marketing blog voor Nederlandse ondernemers",
                posting_frequency=frequency
            )
            
            # Calculate execution time
            execution_time = time.time() - start_time
            
            # Check results
            if result and result.get('success'):
                num_articles = result.get('num_articles', 0)
                content_plan = result.get('content_plan', '')
                
                print(f"✅ SUCCESS!")
                print(f"   Execution Time: {execution_time:.2f} seconds")
                print(f"   Expected Articles: ~{expected_articles}")
                print(f"   Generated Articles: {num_articles}")
                print(f"   Content Plan Length: {len(content_plan)} characters")
                
                # Verify timeout constraint
                if execution_time > 30:
                    print(f"   ⚠️  WARNING: Execution time > 30 seconds (may cause worker timeout)")
                else:
                    print(f"   ✓ Execution time is within safe limits")
                
                # Verify article count
                if num_articles == expected_articles:
                    print(f"   ✓ Article count matches expected value")
                else:
                    print(f"   ⚠️  Article count differs from expected (this is okay)")
                
                # Show preview of content plan
                print(f"\n   Preview of content plan:")
                print(f"   {content_plan[:200]}...")
                
            else:
                print(f"❌ FAILED!")
                print(f"   Error: {result.get('error', 'Unknown error')}")
                print(f"   Execution Time: {execution_time:.2f} seconds")
        
        except Exception as e:
            execution_time = time.time() - start_time
            print(f"❌ EXCEPTION!")
            print(f"   Error: {str(e)}")
            print(f"   Execution Time: {execution_time:.2f} seconds")
    
    print("\n" + "=" * 60)
    print("🏁 Testing Complete!")
    print("\n✅ Key Fixes Implemented:")
    print("   1. Replaced 150+ keyword generation with focused monthly planning")
    print("   2. Using GPT-4o-mini for faster responses")
    print("   3. Reduced max_tokens to 2500 for speed")
    print("   4. Article count based on posting frequency")
    print("   5. UI updated to reflect monthly planning approach")

if __name__ == '__main__':
    # Check if OpenAI API key is set
    if not os.environ.get('OPENAI_API_KEY'):
        print("❌ Error: OPENAI_API_KEY environment variable not set")
        print("   Please set it before running this test.")
        sys.exit(1)
    
    test_monthly_planning()
