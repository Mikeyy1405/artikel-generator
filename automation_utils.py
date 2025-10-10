#!/usr/bin/env python3
"""
Automation Utilities for Content Generation and Publishing
Helper functions for scheduling, planning, and managing automated content

Features:
- Calculate next posting dates based on schedule
- Determine if posting should happen today
- Get posting days for different schedules
- Manage posting queues and priorities
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json


def get_posting_days(schedule: str, custom_days: Optional[str] = None) -> List[str]:
    """
    Get list of posting days for a given schedule
    
    Args:
        schedule: Posting frequency ('daily', '5x_week', '3x_week', 'weekly', 'monthly')
        custom_days: JSON string of custom days for 3x/5x week schedules
        
    Returns:
        List of day names (lowercase): ['monday', 'tuesday', ...]
    """
    all_days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    
    if schedule == 'daily':
        return all_days
    
    elif schedule == '5x_week':
        # Default to weekdays if no custom days provided
        if custom_days:
            try:
                days = json.loads(custom_days)
                return [day.lower() for day in days if day.lower() in all_days]
            except:
                pass
        return ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
    
    elif schedule == '3x_week':
        # Default to Mon/Wed/Fri if no custom days provided
        if custom_days:
            try:
                days = json.loads(custom_days)
                return [day.lower() for day in days if day.lower() in all_days]
            except:
                pass
        return ['monday', 'wednesday', 'friday']
    
    elif schedule == 'weekly':
        # Default to Monday
        if custom_days:
            try:
                days = json.loads(custom_days)
                return [days[0].lower()] if days else ['monday']
            except:
                pass
        return ['monday']
    
    elif schedule == 'monthly':
        # Monthly posts will be handled differently (first of month)
        return []
    
    return []


def should_post_today(website: Dict) -> bool:
    """
    Determine if content should be posted today for this website
    
    Args:
        website: Dictionary with website data including posting_schedule, posting_days, last_post_date
        
    Returns:
        True if posting should happen today, False otherwise
    """
    schedule = website.get('posting_schedule', 'weekly')
    posting_days = website.get('posting_days')
    last_post = website.get('last_post_date')
    
    today = datetime.now()
    today_name = today.strftime('%A').lower()
    
    # Check if we already posted today
    if last_post:
        try:
            last_post_date = datetime.strptime(last_post, '%Y-%m-%d')
            if last_post_date.date() == today.date():
                return False
        except:
            pass
    
    # Monthly schedule - post on first day of month
    if schedule == 'monthly':
        if today.day == 1:
            # Check if we already posted this month
            if last_post:
                try:
                    last_post_date = datetime.strptime(last_post, '%Y-%m-%d')
                    if last_post_date.year == today.year and last_post_date.month == today.month:
                        return False
                except:
                    pass
            return True
        return False
    
    # Get posting days for schedule
    days = get_posting_days(schedule, posting_days)
    
    # Check if today is a posting day
    return today_name in days


def get_next_post_date(website: Dict, from_date: Optional[datetime] = None) -> Optional[datetime]:
    """
    Calculate the next posting date for a website based on its schedule
    
    Args:
        website: Dictionary with website data including posting_schedule, posting_days, last_post_date
        from_date: Calculate from this date (defaults to today)
        
    Returns:
        datetime object for next post date, or None if schedule is invalid
    """
    schedule = website.get('posting_schedule', 'weekly')
    posting_days = website.get('posting_days')
    posting_time = website.get('posting_time', '09:00')
    
    if from_date is None:
        from_date = datetime.now()
    
    # Parse posting time
    try:
        hour, minute = map(int, posting_time.split(':'))
    except:
        hour, minute = 9, 0
    
    # Daily schedule - next day at posting time
    if schedule == 'daily':
        next_date = from_date + timedelta(days=1)
        return next_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
    
    # Monthly schedule - first of next month
    if schedule == 'monthly':
        if from_date.month == 12:
            next_month = from_date.replace(year=from_date.year + 1, month=1, day=1)
        else:
            next_month = from_date.replace(month=from_date.month + 1, day=1)
        return next_month.replace(hour=hour, minute=minute, second=0, microsecond=0)
    
    # Weekly/3x/5x schedules
    days = get_posting_days(schedule, posting_days)
    if not days:
        return None
    
    # Map day names to numbers (0=Monday, 6=Sunday)
    day_map = {
        'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
        'friday': 4, 'saturday': 5, 'sunday': 6
    }
    
    posting_day_nums = sorted([day_map[day] for day in days if day in day_map])
    current_day_num = from_date.weekday()
    
    # Find next posting day
    next_day_num = None
    for day_num in posting_day_nums:
        if day_num > current_day_num:
            next_day_num = day_num
            break
    
    # If no day found this week, use first day of next week
    if next_day_num is None:
        next_day_num = posting_day_nums[0]
        days_ahead = (next_day_num - current_day_num + 7) % 7
        if days_ahead == 0:
            days_ahead = 7
    else:
        days_ahead = next_day_num - current_day_num
    
    next_date = from_date + timedelta(days=days_ahead)
    return next_date.replace(hour=hour, minute=minute, second=0, microsecond=0)


def get_schedule_description(schedule: str, posting_days: Optional[str] = None) -> str:
    """
    Get a human-readable description of a posting schedule
    
    Args:
        schedule: Posting frequency
        posting_days: JSON string of custom days
        
    Returns:
        Human-readable description
    """
    if schedule == 'daily':
        return "Every day"
    elif schedule == 'monthly':
        return "First day of each month"
    elif schedule == 'weekly':
        days = get_posting_days(schedule, posting_days)
        if days:
            return f"Every {days[0].capitalize()}"
        return "Once per week"
    elif schedule == '3x_week':
        days = get_posting_days(schedule, posting_days)
        if days:
            day_names = ', '.join([day.capitalize() for day in days])
            return f"3x per week ({day_names})"
        return "3 times per week"
    elif schedule == '5x_week':
        days = get_posting_days(schedule, posting_days)
        if days:
            day_names = ', '.join([day.capitalize() for day in days])
            return f"5x per week ({day_names})"
        return "5 times per week (weekdays)"
    return "Unknown schedule"


def calculate_monthly_posts(schedule: str) -> int:
    """
    Calculate approximate number of posts per month for a schedule
    
    Args:
        schedule: Posting frequency
        
    Returns:
        Estimated posts per month
    """
    if schedule == 'daily':
        return 30
    elif schedule == '5x_week':
        return 20
    elif schedule == '3x_week':
        return 12
    elif schedule == 'weekly':
        return 4
    elif schedule == 'monthly':
        return 1
    return 0


def get_websites_to_post_today(websites: List[Dict]) -> List[Dict]:
    """
    Filter websites that should post today
    
    Args:
        websites: List of website dictionaries
        
    Returns:
        List of websites that should post today
    """
    return [website for website in websites if should_post_today(website)]


def validate_posting_schedule(schedule: str, posting_days: Optional[str] = None) -> tuple[bool, str]:
    """
    Validate a posting schedule configuration
    
    Args:
        schedule: Posting frequency
        posting_days: JSON string of custom days
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    valid_schedules = ['daily', '5x_week', '3x_week', 'weekly', 'monthly']
    
    if schedule not in valid_schedules:
        return False, f"Invalid schedule. Must be one of: {', '.join(valid_schedules)}"
    
    if schedule in ['3x_week', '5x_week', 'weekly'] and posting_days:
        try:
            days = json.loads(posting_days)
            if not isinstance(days, list):
                return False, "posting_days must be a JSON array"
            
            valid_days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
            for day in days:
                if day.lower() not in valid_days:
                    return False, f"Invalid day: {day}"
            
            if schedule == '3x_week' and len(days) != 3:
                return False, "3x_week schedule requires exactly 3 days"
            
            if schedule == '5x_week' and len(days) != 5:
                return False, "5x_week schedule requires exactly 5 days"
            
            if schedule == 'weekly' and len(days) != 1:
                return False, "weekly schedule requires exactly 1 day"
            
        except json.JSONDecodeError:
            return False, "posting_days must be valid JSON"
    
    return True, ""


def get_next_n_post_dates(website: Dict, n: int = 10) -> List[datetime]:
    """
    Get the next N posting dates for a website
    
    Args:
        website: Website dictionary
        n: Number of dates to generate
        
    Returns:
        List of datetime objects
    """
    dates = []
    current_date = datetime.now()
    
    for _ in range(n):
        next_date = get_next_post_date(website, current_date)
        if next_date:
            dates.append(next_date)
            current_date = next_date
        else:
            break
    
    return dates


if __name__ == '__main__':
    # Example usage
    print("🧪 Testing automation utilities...")
    
    # Test website with 3x per week schedule
    test_website = {
        'id': 1,
        'name': 'Test Blog',
        'posting_schedule': '3x_week',
        'posting_days': '["monday", "wednesday", "friday"]',
        'posting_time': '09:00',
        'last_post_date': None
    }
    
    print(f"\nSchedule: {get_schedule_description(test_website['posting_schedule'], test_website['posting_days'])}")
    print(f"Should post today? {should_post_today(test_website)}")
    print(f"Next post date: {get_next_post_date(test_website)}")
    print(f"Estimated posts per month: {calculate_monthly_posts(test_website['posting_schedule'])}")
    
    print("\nNext 10 posting dates:")
    for i, date in enumerate(get_next_n_post_dates(test_website, 10), 1):
        print(f"  {i}. {date.strftime('%A, %B %d, %Y at %H:%M')}")
    
    print("\n✅ Tests completed!")
