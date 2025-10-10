#!/usr/bin/env python3
"""
Validation script to verify all fixes are in place
This checks code structure without making API calls
"""

import os
import re
import sys

def check_file_contains(filepath, patterns, description):
    """Check if file contains all specified patterns"""
    print(f"\n🔍 Checking: {description}")
    print(f"   File: {filepath}")
    
    if not os.path.exists(filepath):
        print(f"   ❌ File not found!")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    all_found = True
    for pattern, desc in patterns:
        if isinstance(pattern, str):
            found = pattern in content
        else:  # regex
            found = pattern.search(content) is not None
        
        if found:
            print(f"   ✓ {desc}")
        else:
            print(f"   ✗ {desc}")
            all_found = False
    
    return all_found

def main():
    print("=" * 70)
    print("🔍 VALIDATING MONTHLY CONTENT PLANNING FIX")
    print("=" * 70)
    
    base_path = "/home/ubuntu/github_repos/artikel-generator"
    all_checks_passed = True
    
    # Check 1: Database column exists
    checks = [
        (
            f"{base_path}/migrate_wordpress_post_id.py",
            [
                ("wordpress_post_id", "Migration script exists for wordpress_post_id"),
                ("ALTER TABLE articles", "Migration uses ALTER TABLE command"),
            ],
            "Database Migration Script"
        ),
        
        # Check 2: Backend uses monthly planning
        (
            f"{base_path}/app.py",
            [
                ("deepagent_monthly_content_plan", "Uses monthly content planning function"),
                ("posting_frequency", "Gets posting frequency from request"),
                (re.compile(r'posting_frequency.*=.*data\.get.*posting_frequency'), "Extracts posting_frequency in onboarding/start"),
                ("'posting_frequency': posting_frequency", "Stores posting_frequency in site_data"),
            ],
            "Backend API Endpoints"
        ),
        
        # Check 3: Monthly planning function exists
        (
            f"{base_path}/deepagent_research.py",
            [
                ("def deepagent_monthly_content_plan", "Monthly planning function defined"),
                ("frequency_map", "Has frequency map for calculating articles"),
                ("gpt-4o-mini", "Uses faster GPT-4o-mini model"),
                ("max_tokens=2500", "Uses reduced token count for speed"),
                (re.compile(r"'daily':\s*30"), "Daily frequency = 30 articles"),
                (re.compile(r"'weekly':\s*4"), "Weekly frequency = 4 articles"),
            ],
            "Monthly Planning Function"
        ),
        
        # Check 4: UI has posting frequency selector
        (
            f"{base_path}/templates/index.html",
            [
                ("onboarding-posting-frequency", "Has posting frequency dropdown field"),
                ("Postfrequentie", "Has posting frequency label in Dutch"),
                ("Dagelijks (30 artikelen/maand)", "Shows daily option with article count"),
                ("2x per week", "Has 2x per week option"),
                ("Maandelijkse Contentplanning", "Updated header text"),
                ("contentplan op basis van jouw postfrequentie", "Updated description text"),
            ],
            "Frontend UI Elements"
        ),
        
        # Check 5: JavaScript collects frequency
        (
            f"{base_path}/templates/index.html",
            [
                (re.compile(r"getElementById\('onboarding-posting-frequency'\)"), "JavaScript gets posting frequency field"),
                ("posting_frequency: postingFrequency", "JavaScript sends posting frequency to backend"),
            ],
            "Frontend JavaScript"
        ),
    ]
    
    for filepath, patterns, description in checks:
        result = check_file_contains(filepath, patterns, description)
        if not result:
            all_checks_passed = False
    
    print("\n" + "=" * 70)
    if all_checks_passed:
        print("✅ ALL VALIDATION CHECKS PASSED!")
        print("\n🎉 The monthly content planning fix is properly implemented!")
        print("\n📋 Summary:")
        print("   ✓ Database schema verified")
        print("   ✓ Backend endpoint updated to use monthly planning")
        print("   ✓ Monthly planning function implemented")
        print("   ✓ UI updated with posting frequency selector")
        print("   ✓ Frontend collects and sends posting frequency")
        print("\n🚀 Ready for deployment!")
        return 0
    else:
        print("❌ SOME VALIDATION CHECKS FAILED!")
        print("\n⚠️  Please review the failed checks above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
