#!/usr/bin/env python3
"""
Verify database initialization for WritgoAI deployment
"""
import sqlite3
import sys

def verify_database(db_path='writgo_content.db'):
    """Verify all required tables exist"""
    
    required_tables = [
        'users',
        'articles', 
        'websites',
        'website_affiliate_links',
        'website_affiliate_feeds',
        'feed_products',
        'content_plans',
        'wordpress_sites',
        'affiliate_links',
        'knowledge_base',
        'internal_links'
    ]
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        print("📊 Database Verification Report")
        print("=" * 60)
        print(f"\n✓ Database file: {db_path}")
        print(f"✓ Total tables found: {len(existing_tables)}\n")
        
        missing_tables = []
        for table in required_tables:
            if table in existing_tables:
                # Count rows
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"  ✓ {table:30s} ({count} rows)")
            else:
                print(f"  ✗ {table:30s} MISSING!")
                missing_tables.append(table)
        
        conn.close()
        
        if missing_tables:
            print(f"\n❌ Missing tables: {', '.join(missing_tables)}")
            print("\n⚠️  Database needs initialization!")
            return False
        else:
            print("\n✅ All required tables exist!")
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    success = verify_database()
    sys.exit(0 if success else 1)
