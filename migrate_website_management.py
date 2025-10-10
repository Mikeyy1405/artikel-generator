#!/usr/bin/env python3
"""
Migration script to add website management fields
Adds: context, knowledgebase, external_links, niche, target_audience, tone_of_voice
"""
import sqlite3
import sys

def migrate_database(db_path='writgo_content.db'):
    """Add website management columns to websites table"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Add new columns for website management
        columns_to_add = [
            ("niche", "TEXT"),
            ("target_audience", "TEXT"),
            ("tone_of_voice", "TEXT DEFAULT 'professional'"),
            ("context", "TEXT"),
            ("knowledgebase", "TEXT"),  # JSON format
            ("external_links", "TEXT"),  # JSON format
        ]
        
        for column_name, column_type in columns_to_add:
            try:
                cursor.execute(f"ALTER TABLE websites ADD COLUMN {column_name} {column_type}")
                print(f"✓ Added column: {column_name}")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e).lower():
                    print(f"  Column {column_name} already exists, skipping")
                else:
                    raise
        
        conn.commit()
        print("\n✓ Migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"✗ Migration failed: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()

if __name__ == "__main__":
    db_path = sys.argv[1] if len(sys.argv) > 1 else 'writgo_content.db'
    success = migrate_database(db_path)
    sys.exit(0 if success else 1)
