#!/usr/bin/env python3
"""
Database Migration: Add website_id to content_plans table
This fixes the issue where content plans are not properly linked to websites
"""
import sqlite3
from datetime import datetime

DB_PATH = 'writgo_content.db'

def migrate():
    """Add website_id column to content_plans and migrate existing data"""
    print("🔄 Starting migration: Add website_id to content_plans")
    print(f"📁 Database: {DB_PATH}")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Step 1: Add website_id column
        print("\n📝 Step 1: Adding website_id column...")
        try:
            cursor.execute('ALTER TABLE content_plans ADD COLUMN website_id INTEGER')
            print("   ✅ Added website_id column to content_plans")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print("   ⚠️  website_id column already exists, skipping...")
            else:
                raise
        
        # Step 2: Check current state
        print("\n📊 Step 2: Checking current data...")
        cursor.execute('''
            SELECT COUNT(*) FROM content_plans 
            WHERE wordpress_site_id IS NOT NULL AND website_id IS NULL
        ''')
        records_to_update = cursor.fetchone()[0]
        print(f"   📌 Found {records_to_update} content plans to migrate")
        
        # Step 3: Migrate existing records
        if records_to_update > 0:
            print("\n🔄 Step 3: Migrating existing records...")
            cursor.execute('''
                UPDATE content_plans 
                SET website_id = wordpress_site_id 
                WHERE website_id IS NULL AND wordpress_site_id IS NOT NULL
            ''')
            rows_updated = cursor.rowcount
            print(f"   ✅ Updated {rows_updated} content plans with website_id")
        else:
            print("\n✅ Step 3: No records to migrate")
        
        # Step 4: Verify migration
        print("\n🔍 Step 4: Verifying migration...")
        cursor.execute('''
            SELECT 
                COUNT(*) as total,
                COUNT(website_id) as with_website_id,
                COUNT(wordpress_site_id) as with_wordpress_site_id
            FROM content_plans
        ''')
        total, with_website_id, with_wordpress_site_id = cursor.fetchone()
        print(f"   📊 Total content plans: {total}")
        print(f"   📊 With website_id: {with_website_id}")
        print(f"   📊 With wordpress_site_id: {with_wordpress_site_id}")
        
        # Step 5: Show sample data
        print("\n📋 Step 5: Sample migrated data...")
        cursor.execute('''
            SELECT id, title, website_id, wordpress_site_id 
            FROM content_plans 
            LIMIT 5
        ''')
        for row in cursor.fetchall():
            print(f"   ID: {row[0]}, Title: {row[1][:30]}..., website_id: {row[2]}, wordpress_site_id: {row[3]}")
        
        # Commit changes
        conn.commit()
        print("\n✅ Migration completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    print("=" * 60)
    print("DATABASE MIGRATION: content_plans.website_id")
    print("=" * 60)
    migrate()
