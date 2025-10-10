#!/usr/bin/env python3
"""
Database migration script to add Stripe subscription fields
"""
import sqlite3

DB_PATH = 'writgo_content.db'

def migrate_database():
    """Add Stripe subscription fields to users table"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if columns already exist
    cursor.execute("PRAGMA table_info(users)")
    columns = [column[1] for column in cursor.fetchall()]
    
    # Add new columns if they don't exist
    if 'stripe_customer_id' not in columns:
        cursor.execute('ALTER TABLE users ADD COLUMN stripe_customer_id TEXT')
        print("✅ Added stripe_customer_id column")
    
    if 'stripe_subscription_id' not in columns:
        cursor.execute('ALTER TABLE users ADD COLUMN stripe_subscription_id TEXT')
        print("✅ Added stripe_subscription_id column")
    
    if 'subscription_status' not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN subscription_status TEXT DEFAULT 'inactive'")
        print("✅ Added subscription_status column")
    
    if 'subscription_start_date' not in columns:
        cursor.execute('ALTER TABLE users ADD COLUMN subscription_start_date TIMESTAMP')
        print("✅ Added subscription_start_date column")
    
    if 'subscription_end_date' not in columns:
        cursor.execute('ALTER TABLE users ADD COLUMN subscription_end_date TIMESTAMP')
        print("✅ Added subscription_end_date column")
    
    conn.commit()
    conn.close()
    print("\n✅ Database migration completed successfully!")

if __name__ == '__main__':
    migrate_database()
