
"""
Dashboard API Module
Provides comprehensive statistics and data for the WritgoAI dashboard
"""

import sqlite3
from datetime import datetime, timedelta
from collections import defaultdict
import calendar

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect('writgo_content.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_dashboard_stats():
    """
    Get comprehensive dashboard statistics
    Returns all data needed for the dashboard
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get current date info
    now = datetime.now()
    first_day_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    first_day_of_week = now - timedelta(days=now.weekday())
    
    # Basic stats
    stats = {}
    
    # Total articles
    cursor.execute("SELECT COUNT(*) as count FROM articles")
    stats['total_articles'] = cursor.fetchone()['count']
    
    # Articles this month
    cursor.execute("""
        SELECT COUNT(*) as count FROM articles 
        WHERE created_at >= ?
    """, (first_day_of_month.isoformat(),))
    stats['articles_this_month'] = cursor.fetchone()['count']
    
    # Calculate trend (compare with last month)
    last_month = first_day_of_month - timedelta(days=1)
    first_day_last_month = last_month.replace(day=1)
    cursor.execute("""
        SELECT COUNT(*) as count FROM articles 
        WHERE created_at >= ? AND created_at < ?
    """, (first_day_last_month.isoformat(), first_day_of_month.isoformat()))
    last_month_count = cursor.fetchone()['count']
    
    if last_month_count > 0:
        stats['articles_trend'] = round(((stats['articles_this_month'] - last_month_count) / last_month_count) * 100, 1)
    else:
        stats['articles_trend'] = 100 if stats['articles_this_month'] > 0 else 0
    
    # Total words
    cursor.execute("SELECT SUM(word_count) as total FROM articles WHERE word_count IS NOT NULL")
    result = cursor.fetchone()
    stats['total_words'] = result['total'] if result['total'] else 0
    
    # Average words per article
    if stats['total_articles'] > 0:
        stats['avg_words'] = round(stats['total_words'] / stats['total_articles'])
    else:
        stats['avg_words'] = 0
    
    # Words trend (simplified)
    stats['words_trend'] = 15  # Placeholder
    
    # Total websites
    cursor.execute("SELECT COUNT(*) as count FROM websites")
    stats['total_websites'] = cursor.fetchone()['count']
    
    # Websites trend
    stats['websites_trend'] = 10  # Placeholder
    
    # Total affiliate links
    cursor.execute("SELECT COUNT(*) as count FROM affiliate_links")
    stats['total_affiliate_links'] = cursor.fetchone()['count']
    
    # Published count (articles with WordPress post_id)
    cursor.execute("SELECT COUNT(*) as count FROM articles WHERE wordpress_post_id IS NOT NULL")
    stats['published_count'] = cursor.fetchone()['count']
    
    # Published this week
    cursor.execute("""
        SELECT COUNT(*) as count FROM articles 
        WHERE wordpress_post_id IS NOT NULL AND created_at >= ?
    """, (first_day_of_week.isoformat(),))
    stats['published_this_week'] = cursor.fetchone()['count']
    
    # Published trend
    stats['published_trend'] = 20  # Placeholder
    
    # Charts data
    charts = {}
    
    # Articles per month (last 6 months)
    articles_per_month = []
    labels_per_month = []
    
    for i in range(5, -1, -1):
        month_date = now - timedelta(days=30 * i)
        month_start = month_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        if i == 0:
            month_end = now
        else:
            next_month = month_start.replace(day=28) + timedelta(days=4)
            month_end = next_month.replace(day=1) - timedelta(seconds=1)
        
        cursor.execute("""
            SELECT COUNT(*) as count FROM articles 
            WHERE created_at >= ? AND created_at <= ?
        """, (month_start.isoformat(), month_end.isoformat()))
        
        count = cursor.fetchone()['count']
        articles_per_month.append(count)
        labels_per_month.append(calendar.month_abbr[month_start.month])
    
    charts['articles_per_month'] = {
        'labels': labels_per_month,
        'data': articles_per_month
    }
    
    # Words per week (last 8 weeks)
    words_per_week = []
    labels_per_week = []
    
    for i in range(7, -1, -1):
        week_start = now - timedelta(days=7 * i)
        week_end = week_start + timedelta(days=7)
        
        cursor.execute("""
            SELECT SUM(word_count) as total FROM articles 
            WHERE created_at >= ? AND created_at < ?
        """, (week_start.isoformat(), week_end.isoformat()))
        
        result = cursor.fetchone()
        total = result['total'] if result['total'] else 0
        words_per_week.append(total)
        labels_per_week.append(f"Week {week_start.strftime('%d/%m')}")
    
    charts['words_per_week'] = {
        'labels': labels_per_week,
        'data': words_per_week
    }
    
    # Articles per website (using content_plans which has wordpress_site_id)
    cursor.execute("""
        SELECT w.name, COUNT(cp.id) as count 
        FROM websites w 
        LEFT JOIN content_plans cp ON cp.wordpress_site_id = w.id 
        WHERE cp.article_id IS NOT NULL OR cp.wordpress_post_id IS NOT NULL
        GROUP BY w.id, w.name
        ORDER BY count DESC
        LIMIT 6
    """)
    
    website_data = cursor.fetchall()
    charts['articles_per_website'] = {
        'labels': [row['name'] if row['name'] else 'Onbekend' for row in website_data],
        'data': [row['count'] for row in website_data]
    }
    
    # Recent activity
    recent_activity = []
    
    cursor.execute("""
        SELECT title, created_at, word_count, wordpress_post_id 
        FROM articles 
        ORDER BY created_at DESC 
        LIMIT 10
    """)
    
    articles = cursor.fetchall()
    
    for article in articles:
        created = datetime.fromisoformat(article['created_at'])
        time_diff = now - created
        
        if time_diff.days == 0:
            if time_diff.seconds < 3600:
                time_str = f"{time_diff.seconds // 60} min geleden"
            else:
                time_str = f"{time_diff.seconds // 3600} uur geleden"
        elif time_diff.days == 1:
            time_str = "Gisteren"
        else:
            time_str = f"{time_diff.days} dagen geleden"
        
        activity = {
            'icon': '📝',
            'color': 'linear-gradient(135deg, #00AEEF, #004E92)',
            'title': article['title'][:50] + ('...' if len(article['title']) > 50 else ''),
            'meta': f"{article['word_count']} woorden" + (' • Gepubliceerd' if article['wordpress_post_id'] else ''),
            'time': time_str
        }
        recent_activity.append(activity)
    
    # Website overview
    websites = []
    
    cursor.execute("""
        SELECT 
            w.id,
            w.name,
            w.url,
            COUNT(DISTINCT cp.id) as article_count,
            COALESCE(SUM(cp.word_count), 0) as total_words
        FROM websites w
        LEFT JOIN content_plans cp ON cp.wordpress_site_id = w.id
        WHERE cp.article_id IS NOT NULL OR cp.wordpress_post_id IS NOT NULL
        GROUP BY w.id, w.name, w.url
        ORDER BY article_count DESC
        LIMIT 6
    """)
    
    website_rows = cursor.fetchall()
    
    for row in website_rows:
        website = {
            'id': row['id'],
            'name': row['name'] if row['name'] else 'Website',
            'url': row['url'],
            'articles': row['article_count'],
            'words': round((row['total_words'] if row['total_words'] else 0) / 1000, 1)
        }
        websites.append(website)
    
    conn.close()
    
    return {
        'success': True,
        'stats': stats,
        'charts': charts,
        'recent_activity': recent_activity,
        'websites': websites
    }
