#!/usr/bin/env python3
"""
Test script to verify all API endpoints are working correctly
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_wordpress_sites_get():
    """Test GET /api/wordpress-sites"""
    print("\n🧪 Testing GET /api/wordpress-sites...")
    try:
        response = requests.get(f"{BASE_URL}/api/wordpress-sites")
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        assert response.status_code == 200
        assert 'success' in data
        print("✅ PASSED")
    except Exception as e:
        print(f"❌ FAILED: {e}")

def test_wordpress_sites_post():
    """Test POST /api/wordpress-sites"""
    print("\n🧪 Testing POST /api/wordpress-sites...")
    try:
        payload = {
            "site_name": "Test Site",
            "site_url": "https://test.com",
            "username": "testuser",
            "app_password": "test1234"
        }
        response = requests.post(
            f"{BASE_URL}/api/wordpress-sites",
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        assert response.status_code in [200, 400]  # 400 if already exists
        assert 'success' in data or 'error' in data
        print("✅ PASSED")
    except Exception as e:
        print(f"❌ FAILED: {e}")

def test_articles_get():
    """Test GET /api/articles"""
    print("\n🧪 Testing GET /api/articles...")
    try:
        response = requests.get(f"{BASE_URL}/api/articles")
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        assert response.status_code == 200
        assert 'success' in data
        print("✅ PASSED")
    except Exception as e:
        print(f"❌ FAILED: {e}")

def test_404_endpoint():
    """Test 404 error handling"""
    print("\n🧪 Testing 404 error handling...")
    try:
        response = requests.get(f"{BASE_URL}/api/nonexistent")
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        assert response.status_code == 404
        assert 'error' in data
        print("✅ PASSED")
    except Exception as e:
        print(f"❌ FAILED: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("API ENDPOINTS TEST SUITE")
    print("=" * 60)
    
    test_wordpress_sites_get()
    test_wordpress_sites_post()
    test_articles_get()
    test_404_endpoint()
    
    print("\n" + "=" * 60)
    print("TEST SUITE COMPLETED")
    print("=" * 60)
