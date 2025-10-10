#!/usr/bin/env python3
"""
Migration script to add wordpress_post_id column to articles table
This fixes the error: no such column: wordpress_post_id
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = 'writgo_content.db'

def migrate_wordpress_post_id():
    """Add wordpress_post_id column to articles table"""
    
    print("🚀 Starting wordpress_post_id migration...")
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found: {DB_PATH}")
        print(f"   Looking for database at: {os.path.abspath(DB_PATH)}")
        return False
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if column already exists
        print("🔍 Checking current articles table schema...")
        cursor.execute("PRAGMA table_info(articles)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        print(f"📋 Current columns: {', '.join(column_names)}")
        
        if 'wordpress_post_id' in column_names:
            print("✅ wordpress_post_id column already exists!")
            conn.close()
            return True
        
        # Add wordpress_post_id column
        print("➕ Adding wordpress_post_id column to articles table...")
        cursor.execute('''
            ALTER TABLE articles 
            ADD COLUMN wordpress_post_id INTEGER
        ''')
        
        # Add wordpress_url column as well for completeness
        print("➕ Adding wordpress_url column to articles table...")
        cursor.execute('''
            ALTER TABLE articles 
            ADD COLUMN wordpress_url TEXT
        ''')
        
        conn.commit()
        
        # Verify columns were added
        print("🔍 Verifying new columns...")
        cursor.execute("PRAGMA table_info(articles)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if 'wordpress_post_id' in column_names and 'wordpress_url' in column_names:
            print("✅ Columns added successfully!")
            print(f"\n📋 Updated articles table schema:")
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
            
            conn.close()
            return True
        else:
            print("❌ Failed to add columns")
            conn.close()
            return False
            
    except Exception as e:
        print(f"❌ Migration error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = migrate_wordpress_post_id()
    
    if success:
        print("\n✅ Migration completed successfully!")
        print("   The wordpress_post_id column is now available in the articles table.")
    else:
        print("\n❌ Migration failed!")
        print("   Please check the error messages above.")
