#!/usr/bin/env python3
"""
Migration: Add remember_token to users table
This allows users to stay logged in across deployments
"""

import sqlite3
import os

DB_PATH = os.environ.get('DB_PATH', 'writgo.db')

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'remember_token' not in columns:
            print("Adding remember_token column...")
            cursor.execute("ALTER TABLE users ADD COLUMN remember_token TEXT")
            print("✅ Added remember_token column")
        else:
            print("⏭️  remember_token column already exists")
        
        if 'remember_token_expires' not in columns:
            print("Adding remember_token_expires column...")
            cursor.execute("ALTER TABLE users ADD COLUMN remember_token_expires TIMESTAMP")
            print("✅ Added remember_token_expires column")
        else:
            print("⏭️  remember_token_expires column already exists")
        
        conn.commit()
        print("\n✅ Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    migrate()
