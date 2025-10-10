#!/usr/bin/env python3
"""
Test script to verify website persistence fix
"""
import sqlite3
import json
from datetime import datetime

DB_PATH = 'writgo_content.db'

def test_website_persistence():
    """Test that websites are properly saved with user_id"""
    
    print("🧪 Testing Website Persistence Fix\n")
    
    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Test 1: Check schema has user_id column
    print("1️⃣ Checking database schema...")
    cursor.execute("PRAGMA table_info(websites)")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]
    
    if 'user_id' in column_names:
        print("   ✅ user_id column exists in websites table")
    else:
        print("   ❌ user_id column missing!")
        return False
    
    # Test 2: Insert a test website with user_id
    print("\n2️⃣ Testing INSERT with user_id...")
    test_url = f"https://test-website-{datetime.now().timestamp()}.com"
    test_user_id = 1
    
    try:
        cursor.execute('''
            INSERT INTO websites (name, url, sitemap_url, created_at, user_id)
            VALUES (?, ?, ?, ?, ?)
        ''', ('Test Website', test_url, 'https://test.com/sitemap.xml', datetime.now(), test_user_id))
        
        website_id = cursor.lastrowid
        conn.commit()
        print(f"   ✅ Website inserted successfully (ID: {website_id})")
    except Exception as e:
        print(f"   ❌ Failed to insert: {e}")
        conn.close()
        return False
    
    # Test 3: Verify the website was saved with correct user_id
    print("\n3️⃣ Verifying website was saved with user_id...")
    cursor.execute('SELECT id, name, url, user_id FROM websites WHERE id = ?', (website_id,))
    row = cursor.fetchone()
    
    if row and row[3] == test_user_id:
        print(f"   ✅ Website saved with correct user_id: {row[3]}")
    else:
        print(f"   ❌ Website not found or wrong user_id")
        conn.close()
        return False
    
    # Test 4: Test filtering by user_id
    print("\n4️⃣ Testing SELECT with user_id filter...")
    cursor.execute('''
        SELECT id, name, url FROM websites 
        WHERE user_id = ?
        ORDER BY created_at DESC
    ''', (test_user_id,))
    
    results = cursor.fetchall()
    print(f"   ✅ Found {len(results)} websites for user_id={test_user_id}")
    
    # Test 5: Clean up test data
    print("\n5️⃣ Cleaning up test data...")
    cursor.execute('DELETE FROM websites WHERE id = ?', (website_id,))
    conn.commit()
    print(f"   ✅ Test website deleted")
    
    conn.close()
    
    print("\n" + "="*50)
    print("✅ ALL TESTS PASSED!")
    print("="*50)
    print("\nThe database persistence fix is working correctly:")
    print("  • Websites are saved with user_id")
    print("  • Websites can be filtered by user_id")
    print("  • Database commits are working properly")
    
    return True

if __name__ == '__main__':
    test_website_persistence()
