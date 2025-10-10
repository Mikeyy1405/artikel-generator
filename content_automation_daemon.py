#!/usr/bin/env python3
"""
WritgoAI Content Automation Daemon
Automated content generation and publishing system

Features:
- Checks websites due for posting based on schedule
- Generates blog content automatically
- Publishes to WordPress or saves for approval
- Handles errors gracefully with logging
- Sends notifications (optional)

Usage:
    python content_automation_daemon.py [--dry-run] [--website-id ID]
    
Options:
    --dry-run: Test mode, don't actually publish
    --website-id: Process only specific website ID
"""

import os
import sys
import json
import sqlite3
import logging
import argparse
import traceback
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import requests
from pathlib import Path

# Add project directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import project modules
from automation_utils import should_post_today, get_next_post_date
from blog_generator import BlogGenerator

# Configure logging
LOG_DIR = Path(__file__).parent / 'logs'
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / f'automation_daemon_{datetime.now().strftime("%Y%m%d")}.log'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger('ContentAutomationDaemon')

# Database path
DB_PATH = Path(__file__).parent / 'writgo_content.db'

# API secrets path
SECRETS_PATH = Path.home() / '.config' / 'abacusai_auth_secrets.json'


class ContentAutomationDaemon:
    """
    Main daemon class for automated content generation and publishing
    """
    
    def __init__(self, dry_run: bool = False):
        """
        Initialize the daemon
        
        Args:
            dry_run: If True, don't actually publish content
        """
        self.dry_run = dry_run
        self.db_path = DB_PATH
        self.secrets = self._load_secrets()
        self.blog_generator = None
        
        logger.info(f"🚀 Content Automation Daemon initialized (dry_run={dry_run})")
        logger.info(f"📁 Database: {self.db_path}")
        logger.info(f"📝 Log file: {LOG_FILE}")
    
    def _load_secrets(self) -> Dict:
        """Load API secrets from config file"""
        try:
            if SECRETS_PATH.exists():
                with open(SECRETS_PATH, 'r') as f:
                    secrets = json.load(f)
                logger.info("✅ API secrets loaded successfully")
                return secrets
            else:
                logger.warning(f"⚠️ Secrets file not found: {SECRETS_PATH}")
                return {}
        except Exception as e:
            logger.error(f"❌ Error loading secrets: {e}")
            return {}
    
    def _get_api_key(self, service: str, key_name: str) -> Optional[str]:
        """Get API key from secrets"""
        try:
            return self.secrets.get(service, {}).get('secrets', {}).get(key_name, {}).get('value')
        except:
            return None
    
    def _init_blog_generator(self) -> bool:
        """Initialize blog generator with API keys"""
        try:
            pixabay_key = self._get_api_key('pixabay', 'api_key')
            
            if not pixabay_key:
                logger.error("❌ Pixabay API key not found in secrets")
                return False
            
            self.blog_generator = BlogGenerator(
                pixabay_api_key=pixabay_key,
                pexels_api_key=self._get_api_key('pexels', 'api_key'),
                unsplash_access_key=self._get_api_key('unsplash', 'access_key')
            )
            
            logger.info("✅ Blog generator initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error initializing blog generator: {e}")
            return False
    
    def _get_db_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def get_websites_due_for_posting(self, website_id: Optional[int] = None) -> List[Dict]:
        """
        Get all websites that should post today
        
        Args:
            website_id: If provided, only check this specific website
            
        Returns:
            List of website dictionaries
        """
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            
            # Build query
            if website_id:
                query = "SELECT * FROM websites WHERE id = ?"
                cursor.execute(query, (website_id,))
            else:
                query = """
                    SELECT * FROM websites 
                    WHERE posting_schedule IS NOT NULL
                    AND wordpress_url IS NOT NULL
                    AND wordpress_username IS NOT NULL
                    AND wordpress_password IS NOT NULL
                """
                cursor.execute(query)
            
            websites = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            # Filter websites that should post today
            websites_to_post = []
            for website in websites:
                if should_post_today(website):
                    websites_to_post.append(website)
                    logger.info(f"✅ Website due for posting: {website['name']} (ID: {website['id']})")
                else:
                    logger.debug(f"⏭️ Website not due today: {website['name']} (ID: {website['id']})")
            
            logger.info(f"📊 Found {len(websites_to_post)} websites due for posting today")
            return websites_to_post
            
        except Exception as e:
            logger.error(f"❌ Error getting websites: {e}")
            logger.error(traceback.format_exc())
            return []
    
    def get_or_create_content_plan(self, website: Dict) -> Optional[Dict]:
        """
        Get existing content plan for today or create a new one
        
        Args:
            website: Website dictionary
            
        Returns:
            Content plan dictionary or None
        """
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            
            today = datetime.now().strftime('%Y-%m-%d')
            
            # Check if content plan exists for today
            cursor.execute("""
                SELECT * FROM content_plans
                WHERE wordpress_site_id = ?
                AND scheduled_date = ?
                ORDER BY created_at DESC
                LIMIT 1
            """, (website['id'], today))
            
            existing_plan = cursor.fetchone()
            
            if existing_plan:
                logger.info(f"📋 Found existing content plan for {website['name']}")
                conn.close()
                return dict(existing_plan)
            
            # Create new content plan
            logger.info(f"📝 Creating new content plan for {website['name']}")
            
            # Get next keyword from onboarding_sessions
            cursor.execute("""
                SELECT keyword_research_data FROM onboarding_sessions
                WHERE website_id = ?
                ORDER BY created_at DESC
                LIMIT 1
            """, (website['id'],))
            
            session = cursor.fetchone()
            keywords = []
            
            if session and session['keyword_research_data']:
                try:
                    research_data = json.loads(session['keyword_research_data'])
                    keywords = research_data.get('keywords', [])
                except:
                    pass
            
            # Get already used keywords
            cursor.execute("""
                SELECT keyword FROM content_plans
                WHERE wordpress_site_id = ?
                AND keyword IS NOT NULL
            """, (website['id'],))
            
            used_keywords = [row['keyword'] for row in cursor.fetchall()]
            
            # Find next unused keyword
            next_keyword = None
            for keyword in keywords:
                if keyword not in used_keywords:
                    next_keyword = keyword
                    break
            
            if not next_keyword:
                # If all keywords used, start over or use website name
                next_keyword = keywords[0] if keywords else website['name']
            
            # Create content plan
            cursor.execute("""
                INSERT INTO content_plans (
                    user_id,
                    title,
                    keyword,
                    scheduled_date,
                    scheduled_time,
                    wordpress_site_id,
                    word_count,
                    status,
                    auto_generated,
                    approval_status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                website['user_id'],
                f"Blog over {next_keyword}",
                next_keyword,
                today,
                website.get('posting_time', '09:00'),
                website['id'],
                1000,  # Default word count
                'scheduled',
                1,  # auto_generated
                'pending'
            ))
            
            plan_id = cursor.lastrowid
            conn.commit()
            
            # Fetch the created plan
            cursor.execute("SELECT * FROM content_plans WHERE id = ?", (plan_id,))
            new_plan = dict(cursor.fetchone())
            
            conn.close()
            
            logger.info(f"✅ Created content plan ID {plan_id} for keyword: {next_keyword}")
            return new_plan
            
        except Exception as e:
            logger.error(f"❌ Error creating content plan: {e}")
            logger.error(traceback.format_exc())
            return None
    
    def generate_blog_content(self, website: Dict, content_plan: Dict) -> Optional[Dict]:
        """
        Generate blog content using BlogGenerator
        
        Args:
            website: Website dictionary
            content_plan: Content plan dictionary
            
        Returns:
            Generated content dictionary or None
        """
        try:
            if not self.blog_generator:
                if not self._init_blog_generator():
                    return None
            
            logger.info(f"✍️ Generating blog content for: {content_plan['keyword']}")
            
            # Get affiliate config for this website
            affiliate_config = {}
            # TODO: Load from database if stored
            
            # Generate blog
            result = self.blog_generator.generate_blog(
                topic=content_plan['keyword'],
                word_count=content_plan.get('word_count', 1000),
                website_url=website['url'],
                sitemap_url=website.get('sitemap_url'),
                affiliate_config=affiliate_config,
                extra_context=content_plan.get('description', ''),
                model='gpt-4o'
            )
            
            if result.get('success'):
                logger.info(f"✅ Blog content generated successfully")
                logger.info(f"   - Word count: {result['metadata']['word_count']}")
                logger.info(f"   - Images: {result['metadata']['images_count']}")
                logger.info(f"   - Internal links: {result['metadata']['internal_links_count']}")
                logger.info(f"   - Affiliate links: {result['metadata']['affiliate_links_count']}")
                return result
            else:
                logger.error(f"❌ Blog generation failed: {result.get('error')}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error generating blog content: {e}")
            logger.error(traceback.format_exc())
            return None
    
    def publish_to_wordpress(self, website: Dict, content_plan: Dict, blog_content: Dict) -> bool:
        """
        Publish blog content to WordPress
        
        Args:
            website: Website dictionary
            content_plan: Content plan dictionary
            blog_content: Generated blog content
            
        Returns:
            True if published successfully, False otherwise
        """
        try:
            if self.dry_run:
                logger.info("🧪 DRY RUN: Would publish to WordPress")
                return True
            
            logger.info(f"📤 Publishing to WordPress: {website['wordpress_url']}")
            
            # Prepare WordPress API request
            api_url = f"{website['wordpress_url'].rstrip('/')}/wp-json/wp/v2/posts"
            
            # Create post data
            post_data = {
                'title': content_plan['title'],
                'content': blog_content['content'],
                'status': 'publish',  # or 'draft' if auto_publish is False
                'author': 1,
                'format': 'standard'
            }
            
            # Make API request
            response = requests.post(
                api_url,
                json=post_data,
                auth=(website['wordpress_username'], website['wordpress_password']),
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                post_id = response.json().get('id')
                logger.info(f"✅ Published to WordPress successfully (Post ID: {post_id})")
                
                # Update content plan with WordPress post ID
                conn = self._get_db_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE content_plans
                    SET wordpress_post_id = ?,
                        approval_status = 'published',
                        status = 'published',
                        generated_content = ?
                    WHERE id = ?
                """, (str(post_id), blog_content['content'], content_plan['id']))
                conn.commit()
                conn.close()
                
                return True
            else:
                logger.error(f"❌ WordPress API error: {response.status_code}")
                logger.error(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error publishing to WordPress: {e}")
            logger.error(traceback.format_exc())
            return False
    
    def save_for_approval(self, content_plan: Dict, blog_content: Dict) -> bool:
        """
        Save generated content for manual approval
        
        Args:
            content_plan: Content plan dictionary
            blog_content: Generated blog content
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            logger.info(f"💾 Saving content for approval")
            
            conn = self._get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE content_plans
                SET generated_content = ?,
                    approval_status = 'pending_approval',
                    status = 'ready'
                WHERE id = ?
            """, (blog_content['content'], content_plan['id']))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Content saved for approval")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saving content: {e}")
            logger.error(traceback.format_exc())
            return False
    
    def update_website_post_date(self, website: Dict) -> bool:
        """
        Update website's last_post_date
        
        Args:
            website: Website dictionary
            
        Returns:
            True if updated successfully, False otherwise
        """
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            
            conn = self._get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE websites
                SET last_post_date = ?
                WHERE id = ?
            """, (today, website['id']))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Updated last_post_date for {website['name']}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating website: {e}")
            return False
    
    def process_website(self, website: Dict) -> bool:
        """
        Process a single website: generate and publish content
        
        Args:
            website: Website dictionary
            
        Returns:
            True if processed successfully, False otherwise
        """
        try:
            logger.info(f"\n{'='*80}")
            logger.info(f"🌐 Processing website: {website['name']} (ID: {website['id']})")
            logger.info(f"{'='*80}")
            
            # Step 1: Get or create content plan
            content_plan = self.get_or_create_content_plan(website)
            if not content_plan:
                logger.error(f"❌ Failed to get/create content plan")
                return False
            
            # Step 2: Generate blog content
            blog_content = self.generate_blog_content(website, content_plan)
            if not blog_content:
                logger.error(f"❌ Failed to generate blog content")
                return False
            
            # Step 3: Publish or save for approval
            if website.get('auto_publish', 0) == 1:
                success = self.publish_to_wordpress(website, content_plan, blog_content)
            else:
                success = self.save_for_approval(content_plan, blog_content)
            
            if not success:
                logger.error(f"❌ Failed to publish/save content")
                return False
            
            # Step 4: Update website's last_post_date
            self.update_website_post_date(website)
            
            logger.info(f"✅ Successfully processed website: {website['name']}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error processing website {website['name']}: {e}")
            logger.error(traceback.format_exc())
            return False
    
    def run(self, website_id: Optional[int] = None) -> Dict:
        """
        Main daemon run method
        
        Args:
            website_id: If provided, only process this website
            
        Returns:
            Dictionary with run statistics
        """
        start_time = datetime.now()
        logger.info(f"\n{'#'*80}")
        logger.info(f"🚀 CONTENT AUTOMATION DAEMON STARTED")
        logger.info(f"⏰ Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"{'#'*80}\n")
        
        stats = {
            'start_time': start_time,
            'websites_checked': 0,
            'websites_processed': 0,
            'websites_failed': 0,
            'content_generated': 0,
            'content_published': 0,
            'content_pending': 0,
            'errors': []
        }
        
        try:
            # Get websites due for posting
            websites = self.get_websites_due_for_posting(website_id)
            stats['websites_checked'] = len(websites)
            
            if not websites:
                logger.info("ℹ️ No websites due for posting today")
                return stats
            
            # Process each website
            for website in websites:
                try:
                    success = self.process_website(website)
                    
                    if success:
                        stats['websites_processed'] += 1
                        stats['content_generated'] += 1
                        
                        if website.get('auto_publish', 0) == 1:
                            stats['content_published'] += 1
                        else:
                            stats['content_pending'] += 1
                    else:
                        stats['websites_failed'] += 1
                        stats['errors'].append(f"Failed to process {website['name']}")
                        
                except Exception as e:
                    stats['websites_failed'] += 1
                    error_msg = f"Error processing {website['name']}: {str(e)}"
                    stats['errors'].append(error_msg)
                    logger.error(f"❌ {error_msg}")
            
        except Exception as e:
            error_msg = f"Fatal error in daemon run: {str(e)}"
            stats['errors'].append(error_msg)
            logger.error(f"❌ {error_msg}")
            logger.error(traceback.format_exc())
        
        finally:
            # Log final statistics
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            logger.info(f"\n{'#'*80}")
            logger.info(f"📊 DAEMON RUN COMPLETED")
            logger.info(f"⏱️ Duration: {duration:.2f} seconds")
            logger.info(f"{'#'*80}")
            logger.info(f"📈 Statistics:")
            logger.info(f"   - Websites checked: {stats['websites_checked']}")
            logger.info(f"   - Websites processed: {stats['websites_processed']}")
            logger.info(f"   - Websites failed: {stats['websites_failed']}")
            logger.info(f"   - Content generated: {stats['content_generated']}")
            logger.info(f"   - Content published: {stats['content_published']}")
            logger.info(f"   - Content pending approval: {stats['content_pending']}")
            
            if stats['errors']:
                logger.info(f"❌ Errors ({len(stats['errors'])}):")
                for error in stats['errors']:
                    logger.info(f"   - {error}")
            
            logger.info(f"{'#'*80}\n")
            
            stats['end_time'] = end_time
            stats['duration'] = duration
            
        return stats


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='WritgoAI Content Automation Daemon'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Test mode - don\'t actually publish content'
    )
    parser.add_argument(
        '--website-id',
        type=int,
        help='Process only specific website ID'
    )
    
    args = parser.parse_args()
    
    # Create and run daemon
    daemon = ContentAutomationDaemon(dry_run=args.dry_run)
    stats = daemon.run(website_id=args.website_id)
    
    # Exit with appropriate code
    if stats['websites_failed'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
