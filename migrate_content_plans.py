
#!/usr/bin/env python3
"""
Migration script to add content_plans table
Run this script to add the content planning feature to the database
"""

import sqlite3
from datetime import datetime

DB_PATH = 'writgo_content.db'

def migrate():
    """Add content_plans table to database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Create content_plans table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS content_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL DEFAULT 1,
                title TEXT NOT NULL,
                description TEXT,
                keyword TEXT,
                target_date DATE,
                status TEXT DEFAULT 'draft',
                article_id INTEGER,
                wordpress_site_id INTEGER,
                word_count INTEGER DEFAULT 1000,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE SET NULL,
                FOREIGN KEY (wordpress_site_id) REFERENCES wordpress_sites(id) ON DELETE SET NULL
            )
        ''')
        
        print("✅ content_plans table created successfully")
        
        # Create index for faster queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_content_plans_user_id 
            ON content_plans(user_id)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_content_plans_target_date 
            ON content_plans(target_date)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_content_plans_status 
            ON content_plans(status)
        ''')
        
        print("✅ Indexes created successfully")
        
        conn.commit()
        print("✅ Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    migrate()
