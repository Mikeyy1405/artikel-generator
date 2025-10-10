#!/usr/bin/env python3
"""
Migration script to add onboarding_sessions table
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = 'writgo_content.db'

def migrate_onboarding_table():
    """Add onboarding_sessions table for tracking onboarding flow"""
    
    print("🚀 Starting onboarding table migration...")
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found: {DB_PATH}")
        return False
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Create onboarding_sessions table
        print("📊 Creating onboarding_sessions table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS onboarding_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL DEFAULT 1,
                website_id INTEGER,
                current_step TEXT DEFAULT 'website_added',
                status TEXT DEFAULT 'in_progress',
                site_data TEXT,
                keyword_research_data TEXT,
                content_plan_data TEXT,
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (website_id) REFERENCES websites(id) ON DELETE CASCADE
            )
        ''')
        
        # Create indexes
        print("🔍 Creating indexes...")
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_onboarding_user_id 
            ON onboarding_sessions(user_id)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_onboarding_status 
            ON onboarding_sessions(status)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_onboarding_website_id 
            ON onboarding_sessions(website_id)
        ''')
        
        conn.commit()
        
        # Verify table creation
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='onboarding_sessions'
        """)
        
        if cursor.fetchone():
            print("✅ onboarding_sessions table created successfully!")
            
            # Show table schema
            cursor.execute("PRAGMA table_info(onboarding_sessions)")
            columns = cursor.fetchall()
            print("\n📋 Table schema:")
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
            
            conn.close()
            return True
        else:
            print("❌ Failed to create onboarding_sessions table")
            conn.close()
            return False
            
    except Exception as e:
        print(f"❌ Migration error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = migrate_onboarding_table()
    
    if success:
        print("\n✅ Migration completed successfully!")
    else:
        print("\n❌ Migration failed!")
