#!/usr/bin/env python3
"""
Migration script to add automation features for content generation and publishing
This script is idempotent and can be run multiple times safely

FEATURES:
- Automated content generation scheduling
- Configurable posting frequency (daily, 5x/week, 3x/week, weekly, monthly)
- Optional approval workflow
- WordPress integration per website
- Content plan scheduling and status tracking

Run: python3 migrate_automation.py
"""

import sqlite3
from datetime import datetime
import json

DB_PATH = 'writgo_content.db'

def column_exists(cursor, table_name, column_name):
    """Check if a column exists in a table"""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    return column_name in columns

def migrate_websites_table(cursor):
    """Extend websites table with automation configuration columns"""
    print("\n📊 Migrating websites table...")
    
    columns_to_add = [
        ('posting_schedule', 'TEXT DEFAULT "weekly"', 'Posting frequency schedule'),
        ('posting_days', 'TEXT', 'JSON array of posting days for 3x/5x week'),
        ('posting_time', 'TEXT DEFAULT "09:00"', 'Time of day to publish'),
        ('auto_publish', 'INTEGER DEFAULT 0', 'Auto-publish without approval (0/1)'),
        ('last_post_date', 'TEXT', 'Last publication date for tracking'),
        ('wordpress_url', 'TEXT', 'WordPress site URL'),
        ('wordpress_username', 'TEXT', 'WordPress username'),
        ('wordpress_password', 'TEXT', 'WordPress app password'),
    ]
    
    added_count = 0
    for column_name, column_def, description in columns_to_add:
        if not column_exists(cursor, 'websites', column_name):
            try:
                cursor.execute(f'ALTER TABLE websites ADD COLUMN {column_name} {column_def}')
                print(f"  ✅ Added column: {column_name} ({description})")
                added_count += 1
            except sqlite3.OperationalError as e:
                print(f"  ⚠️  Could not add {column_name}: {e}")
        else:
            print(f"  ⏭️  Column already exists: {column_name}")
    
    # Set default values for existing records
    cursor.execute("SELECT COUNT(*) FROM websites WHERE posting_schedule IS NULL")
    null_count = cursor.fetchone()[0]
    
    if null_count > 0:
        cursor.execute("""
            UPDATE websites 
            SET posting_schedule = 'weekly',
                posting_time = '09:00',
                auto_publish = 0
            WHERE posting_schedule IS NULL
        """)
        print(f"  ✅ Set default values for {null_count} existing records")
    
    return added_count

def migrate_content_plans_table(cursor):
    """Extend content_plans table with scheduling and publishing columns"""
    print("\n📊 Migrating content_plans table...")
    
    columns_to_add = [
        ('scheduled_date', 'TEXT', 'When to publish (date)'),
        ('scheduled_time', 'TEXT', 'When to publish (time)'),
        ('auto_generated', 'INTEGER DEFAULT 0', 'Is this auto-generated (0/1)'),
        ('approval_status', 'TEXT', 'Approval status: pending/approved/rejected/published'),
        ('generated_content', 'TEXT', 'The generated blog content HTML'),
        ('wordpress_post_id', 'TEXT', 'WordPress post ID after publication'),
    ]
    
    added_count = 0
    for column_name, column_def, description in columns_to_add:
        if not column_exists(cursor, 'content_plans', column_name):
            try:
                cursor.execute(f'ALTER TABLE content_plans ADD COLUMN {column_name} {column_def}')
                print(f"  ✅ Added column: {column_name} ({description})")
                added_count += 1
            except sqlite3.OperationalError as e:
                print(f"  ⚠️  Could not add {column_name}: {e}")
        else:
            print(f"  ⏭️  Column already exists: {column_name}")
    
    return added_count

def create_indexes(cursor):
    """Create indexes for better query performance"""
    print("\n🔍 Creating indexes...")
    
    indexes = [
        ('idx_websites_posting_schedule', 'websites', 'posting_schedule'),
        ('idx_websites_last_post_date', 'websites', 'last_post_date'),
        ('idx_websites_auto_publish', 'websites', 'auto_publish'),
        ('idx_content_plans_scheduled_date', 'content_plans', 'scheduled_date'),
        ('idx_content_plans_approval_status', 'content_plans', 'approval_status'),
        ('idx_content_plans_auto_generated', 'content_plans', 'auto_generated'),
    ]
    
    for index_name, table_name, column_name in indexes:
        try:
            cursor.execute(f'''
                CREATE INDEX IF NOT EXISTS {index_name}
                ON {table_name}({column_name})
            ''')
            print(f"  ✅ Created index: {index_name}")
        except Exception as e:
            print(f"  ⚠️  Could not create index {index_name}: {e}")

def verify_migration(cursor):
    """Verify that all columns were added successfully"""
    print("\n✅ Verifying migration...")
    
    # Check websites table
    cursor.execute("PRAGMA table_info(websites)")
    websites_columns = [row[1] for row in cursor.fetchall()]
    
    required_websites_cols = [
        'posting_schedule', 'posting_days', 'posting_time', 'auto_publish',
        'last_post_date', 'wordpress_url', 'wordpress_username', 'wordpress_password'
    ]
    
    websites_ok = all(col in websites_columns for col in required_websites_cols)
    
    # Check content_plans table
    cursor.execute("PRAGMA table_info(content_plans)")
    content_plans_columns = [row[1] for row in cursor.fetchall()]
    
    required_content_plans_cols = [
        'scheduled_date', 'scheduled_time', 'auto_generated',
        'approval_status', 'generated_content', 'wordpress_post_id'
    ]
    
    content_plans_ok = all(col in content_plans_columns for col in required_content_plans_cols)
    
    if websites_ok:
        print(f"  ✅ websites table: All {len(required_websites_cols)} automation columns present")
    else:
        print(f"  ❌ websites table: Missing columns")
        
    if content_plans_ok:
        print(f"  ✅ content_plans table: All {len(required_content_plans_cols)} automation columns present")
    else:
        print(f"  ❌ content_plans table: Missing columns")
    
    return websites_ok and content_plans_ok

def migrate():
    """Run the complete migration"""
    print("=" * 70)
    print("🚀 AUTOMATION MIGRATION SCRIPT")
    print("=" * 70)
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📂 Database: {DB_PATH}")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Migrate both tables
        websites_added = migrate_websites_table(cursor)
        content_plans_added = migrate_content_plans_table(cursor)
        
        # Create indexes
        create_indexes(cursor)
        
        # Verify migration
        success = verify_migration(cursor)
        
        # Commit changes
        conn.commit()
        
        print("\n" + "=" * 70)
        print("📊 MIGRATION SUMMARY")
        print("=" * 70)
        print(f"✅ websites table: {websites_added} new columns added")
        print(f"✅ content_plans table: {content_plans_added} new columns added")
        print(f"✅ Overall status: {'SUCCESS' if success else 'PARTIAL'}")
        print("=" * 70)
        
        if success:
            print("\n🎉 Migration completed successfully!")
            print("\n📝 Next steps:")
            print("   1. Update your app.py init_db() function")
            print("   2. Create automation_utils.py with helper functions")
            print("   3. Implement the scheduling daemon")
            print("   4. Test the automation workflow")
        else:
            print("\n⚠️  Migration completed with warnings. Check the logs above.")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    migrate()
