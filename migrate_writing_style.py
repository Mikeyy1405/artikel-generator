#!/usr/bin/env python3
"""
Migration: Add writing style and affiliate feeds to users table
"""
import sqlite3

DB_PATH = 'writgo_content.db'

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if columns already exist
    cursor.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in cursor.fetchall()]
    
    # Add writing style fields
    if 'writing_style' not in columns:
        print("Adding writing_style column...")
        cursor.execute('''
            ALTER TABLE users ADD COLUMN writing_style TEXT DEFAULT NULL
        ''')
    
    if 'writing_tone' not in columns:
        print("Adding writing_tone column...")
        cursor.execute('''
            ALTER TABLE users ADD COLUMN writing_tone TEXT DEFAULT 'professioneel'
        ''')
    
    if 'target_audience' not in columns:
        print("Adding target_audience column...")
        cursor.execute('''
            ALTER TABLE users ADD COLUMN target_audience TEXT DEFAULT NULL
        ''')
    
    if 'writing_examples' not in columns:
        print("Adding writing_examples column...")
        cursor.execute('''
            ALTER TABLE users ADD COLUMN writing_examples TEXT DEFAULT NULL
        ''')
    
    # Add affiliate feeds fields
    if 'bol_client_id' not in columns:
        print("Adding bol_client_id column...")
        cursor.execute('''
            ALTER TABLE users ADD COLUMN bol_client_id TEXT DEFAULT NULL
        ''')
    
    if 'bol_client_secret' not in columns:
        print("Adding bol_client_secret column...")
        cursor.execute('''
            ALTER TABLE users ADD COLUMN bol_client_secret TEXT DEFAULT NULL
        ''')
    
    if 'tradetracker_id' not in columns:
        print("Adding tradetracker_id column...")
        cursor.execute('''
            ALTER TABLE users ADD COLUMN tradetracker_id TEXT DEFAULT NULL
        ''')
    
    if 'tradetracker_api_key' not in columns:
        print("Adding tradetracker_api_key column...")
        cursor.execute('''
            ALTER TABLE users ADD COLUMN tradetracker_api_key TEXT DEFAULT NULL
        ''')
    
    if 'daisycon_id' not in columns:
        print("Adding daisycon_id column...")
        cursor.execute('''
            ALTER TABLE users ADD COLUMN daisycon_id TEXT DEFAULT NULL
        ''')
    
    if 'custom_affiliate_links' not in columns:
        print("Adding custom_affiliate_links column...")
        cursor.execute('''
            ALTER TABLE users ADD COLUMN custom_affiliate_links TEXT DEFAULT NULL
        ''')
    
    conn.commit()
    conn.close()
    print("✅ Migration completed successfully!")

if __name__ == '__main__':
    migrate()
