#!/usr/bin/env python3
"""Test script for keyword research endpoint"""

import requests
import json

BASE_URL = "http://localhost:5000"

# Test 1: Create onboarding session
print("🧪 Test 1: Creating onboarding session...")
import time
import random

# Generate unique URL
unique_id = int(time.time())
random_suffix = random.randint(1000, 9999)

response = requests.post(f"{BASE_URL}/api/onboarding/start", json={
    "website_name": f"Test Website {unique_id}",
    "website_url": f"https://example-{unique_id}-{random_suffix}.com",
    "sitemap_url": f"https://example-{unique_id}-{random_suffix}.com/sitemap.xml",
    "country": "Nederland",
    "language": "Dutch",
    "description": "Test website for keyword research",
    "wordpress_url": "",
    "wordpress_username": "",
    "wordpress_password": ""
})

if response.status_code == 200:
    data = response.json()
    if data.get('success'):
        onboarding_id = data.get('onboarding_id')
        print(f"✅ Onboarding session created: ID={onboarding_id}")
        
        # Test 2: Run keyword research
        print(f"\n🧪 Test 2: Running keyword research for session {onboarding_id}...")
        response2 = requests.post(f"{BASE_URL}/api/onboarding/keyword-research/{onboarding_id}")
        
        print(f"Status code: {response2.status_code}")
        print(f"Response headers: {dict(response2.headers)}")
        
        try:
            data2 = response2.json()
            print(f"✅ Response is valid JSON")
            print(f"Success: {data2.get('success')}")
            if data2.get('success'):
                print(f"Keywords generated: {data2.get('total_keywords')}")
                print(f"Current step: {data2.get('current_step')}")
            else:
                print(f"Error: {data2.get('error')}")
        except Exception as e:
            print(f"❌ Failed to parse JSON: {e}")
            print(f"Response text: {response2.text[:500]}")
    else:
        print(f"❌ Failed to create onboarding session: {data.get('error')}")
else:
    print(f"❌ Request failed with status {response.status_code}")
    print(f"Response: {response.text}")
