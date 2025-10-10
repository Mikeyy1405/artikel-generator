#!/usr/bin/env python3
"""
Website Management API Endpoints
Handles comprehensive website settings including context, knowledgebase, and external links
"""
import sqlite3
import json
from datetime import datetime
from flask import jsonify, request

DB_PATH = 'writgo_content.db'

def get_website_management(website_id, user_id):
    """Get comprehensive website management data"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get all website data
        cursor.execute('''
            SELECT * FROM websites
            WHERE id = ? AND user_id = ?
        ''', (website_id, user_id))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None, "Website niet gevonden"
        
        # Convert to dict
        website = dict(row)
        
        # Parse JSON fields
        if website.get('external_links'):
            try:
                website['external_links'] = json.loads(website['external_links'])
            except:
                website['external_links'] = []
        else:
            website['external_links'] = []
        
        if website.get('knowledgebase'):
            try:
                website['knowledgebase'] = json.loads(website['knowledgebase'])
            except:
                website['knowledgebase'] = {}
        else:
            website['knowledgebase'] = {}
        
        # Parse posting_days if it exists
        if website.get('posting_days'):
            try:
                website['posting_days'] = json.loads(website['posting_days'])
            except:
                website['posting_days'] = []
        else:
            website['posting_days'] = []
        
        return website, None
        
    except Exception as e:
        return None, str(e)


def update_website_management(website_id, user_id, data):
    """Update comprehensive website management data"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Build dynamic UPDATE query based on provided fields
        update_fields = []
        update_values = []
        
        # Basic info
        if 'name' in data:
            update_fields.append('name = ?')
            update_values.append(data['name'])
        
        if 'niche' in data:
            update_fields.append('niche = ?')
            update_values.append(data['niche'])
        
        if 'target_audience' in data:
            update_fields.append('target_audience = ?')
            update_values.append(data['target_audience'])
        
        if 'tone_of_voice' in data:
            update_fields.append('tone_of_voice = ?')
            update_values.append(data['tone_of_voice'])
        
        # Context & Knowledgebase
        if 'context' in data:
            update_fields.append('context = ?')
            update_values.append(data['context'])
        
        if 'knowledgebase' in data:
            # Convert dict to JSON string
            kb_json = json.dumps(data['knowledgebase'])
            update_fields.append('knowledgebase = ?')
            update_values.append(kb_json)
        
        # External Links
        if 'external_links' in data:
            # Convert list to JSON string
            links_json = json.dumps(data['external_links'])
            update_fields.append('external_links = ?')
            update_values.append(links_json)
        
        # Posting schedule
        if 'posting_schedule' in data:
            update_fields.append('posting_schedule = ?')
            update_values.append(data['posting_schedule'])
        
        if 'posting_days' in data:
            # Convert to JSON string if it's a list
            if isinstance(data['posting_days'], list):
                posting_days_json = json.dumps(data['posting_days'])
            else:
                posting_days_json = data['posting_days']
            update_fields.append('posting_days = ?')
            update_values.append(posting_days_json)
        
        if 'posting_time' in data:
            update_fields.append('posting_time = ?')
            update_values.append(data['posting_time'])
        
        if 'auto_publish' in data:
            update_fields.append('auto_publish = ?')
            update_values.append(1 if data['auto_publish'] else 0)
        
        # WordPress credentials
        if 'wordpress_url' in data:
            update_fields.append('wordpress_url = ?')
            update_values.append(data['wordpress_url'])
        
        if 'wordpress_username' in data:
            update_fields.append('wordpress_username = ?')
            update_values.append(data['wordpress_username'])
        
        if 'wordpress_password' in data:
            update_fields.append('wordpress_password = ?')
            update_values.append(data['wordpress_password'])
        
        # Build and execute query
        if update_fields:
            query = f"UPDATE websites SET {', '.join(update_fields)} WHERE id = ? AND user_id = ?"
            update_values.extend([website_id, user_id])
            
            cursor.execute(query, update_values)
            
            if cursor.rowcount == 0:
                conn.close()
                return False, "Website niet gevonden of geen toegang"
            
            conn.commit()
        
        conn.close()
        
        print(f"✅ Website management updated for website {website_id}")
        return True, None
        
    except Exception as e:
        print(f"❌ Error updating website management: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, str(e)
