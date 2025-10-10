#!/usr/bin/env python3
"""
Database migration script to add user authentication
"""
import sqlite3
import hashlib
import os

DB_PATH = 'writgo_content.db'

def migrate():
    print("🔄 Starting database migration...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if users table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    users_exists = cursor.fetchone() is not None
    
    if not users_exists:
        print("📝 Creating users table...")
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                full_name TEXT,
                is_superuser BOOLEAN DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')
        print("✅ Users table created")
    
    # Add user_id columns to existing tables
    tables_to_update = ['articles', 'wordpress_sites', 'websites']
    
    for table in tables_to_update:
        try:
            cursor.execute(f"SELECT user_id FROM {table} LIMIT 1")
            print(f"✓ {table} already has user_id column")
        except sqlite3.OperationalError:
            print(f"📝 Adding user_id to {table}...")
            cursor.execute(f'ALTER TABLE {table} ADD COLUMN user_id INTEGER NOT NULL DEFAULT 1')
            print(f"✅ Added user_id to {table}")
    
    # Add new user profile columns
    user_columns = [
        ('company', 'TEXT'),
        ('website', 'TEXT'),
        ('facebook', 'TEXT'),
        ('instagram', 'TEXT'),
        ('twitter', 'TEXT'),
        ('linkedin', 'TEXT'),
        ('youtube', 'TEXT'),
        ('tiktok', 'TEXT'),
        ('include_socials', 'BOOLEAN DEFAULT 1'),
        ('auto_images', 'BOOLEAN DEFAULT 1'),
        ('auto_internal_links', 'BOOLEAN DEFAULT 1'),
        ('seo_optimize', 'BOOLEAN DEFAULT 1'),
        ('default_tone', 'TEXT DEFAULT "professional"')
    ]
    
    for column_name, column_type in user_columns:
        try:
            cursor.execute(f"SELECT {column_name} FROM users LIMIT 1")
            print(f"✓ users.{column_name} already exists")
        except sqlite3.OperationalError:
            print(f"📝 Adding {column_name} to users...")
            cursor.execute(f'ALTER TABLE users ADD COLUMN {column_name} {column_type}')
            print(f"✅ Added {column_name} to users")
    
    # Create superuser if not exists
    cursor.execute('SELECT COUNT(*) FROM users WHERE email = ?', ('info@writgo.nl',))
    if cursor.fetchone()[0] == 0:
        print("📝 Creating superuser...")
        password_hash = hashlib.sha256('WritgoAI2025!'.encode()).hexdigest()
        cursor.execute('''
            INSERT INTO users (email, password_hash, full_name, is_superuser, is_active)
            VALUES (?, ?, ?, ?, ?)
        ''', ('info@writgo.nl', password_hash, 'WritgoAI Admin', 1, 1))
        print("✅ Superuser created: info@writgo.nl")
        print("🔑 Password: WritgoAI2025!")
    else:
        print("✓ Superuser already exists")
    
    conn.commit()
    conn.close()
    
    print("\n✅ Migration completed successfully!")
    print("\n📋 Login credentials:")
    print("   Email: info@writgo.nl")
    print("   Password: WritgoAI2025!")

if __name__ == '__main__':
    migrate()
