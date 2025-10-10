# Website Persistence Fix

## Problem Description
Users reported that when they added a website, it would disappear after every update/refresh. This was a database persistence issue where website data was not being properly associated with the logged-in user.

## Root Cause Analysis

The issue was in the `/api/websites` endpoint in `app.py`:

1. **Missing user_id in INSERT**: When adding a new website (POST request), the `user_id` field was not included in the INSERT statement, causing it to use the default value of 1.

2. **Missing user_id filter in SELECT**: When fetching websites (GET request), the query was not filtering by `user_id`, returning ALL websites from ALL users.

3. **Security vulnerability**: Other endpoints (GET, PUT, DELETE, refresh-sitemap) were not filtering by `user_id`, allowing users to potentially access or modify other users' websites.

## Changes Made

### 1. Fixed POST /api/websites (Line 3876-3935)
**Before:**
```python
cursor.execute('''
    INSERT INTO websites (name, url, sitemap_url, created_at)
    VALUES (?, ?, ?, ?)
''', (name, url, sitemap_url, datetime.now()))
```

**After:**
```python
# Get current user
user = get_current_user()
user_id = user.get('id', 1)

cursor.execute('''
    INSERT INTO websites (name, url, sitemap_url, created_at, user_id)
    VALUES (?, ?, ?, ?, ?)
''', (name, url, sitemap_url, datetime.now(), user_id))
```

### 2. Fixed GET /api/websites (Line 3833-3874)
**Before:**
```python
cursor.execute('''
    SELECT id, name, url, sitemap_url, urls_count, last_updated, created_at
    FROM websites
    ORDER BY created_at DESC
''')
```

**After:**
```python
# Get current user
user = get_current_user()
user_id = user.get('id', 1)

cursor.execute('''
    SELECT id, name, url, sitemap_url, urls_count, last_updated, created_at
    FROM websites
    WHERE user_id = ?
    ORDER BY created_at DESC
''', (user_id,))
```

### 3. Fixed GET /api/websites/<website_id> (Line 3942-3989)
Added `user_id` filter to prevent users from accessing other users' websites:
```python
cursor.execute('''
    SELECT id, name, url, sitemap_url, sitemap_urls, urls_count, last_updated, created_at
    FROM websites
    WHERE id = ? AND user_id = ?
''', (website_id, user_id))
```

### 4. Fixed PUT /api/websites/<website_id> (Line 3991-4037)
Added `user_id` filter to prevent users from updating other users' websites:
```python
cursor.execute('''
    UPDATE websites
    SET name = ?, url = ?
    WHERE id = ? AND user_id = ?
''', (name, url, website_id, user_id))
```

### 5. Fixed DELETE /api/websites/<website_id> (Line 4039-4071)
Added `user_id` filter to prevent users from deleting other users' websites:
```python
cursor.execute('DELETE FROM websites WHERE id = ? AND user_id = ?', (website_id, user_id))
```

### 6. Fixed POST /api/websites/<website_id>/refresh-sitemap (Line 4074-4137)
Added `user_id` filter to all database operations:
```python
cursor.execute('SELECT url, sitemap_url FROM websites WHERE id = ? AND user_id = ?', (website_id, user_id))
```

## Testing

A test script was created (`test_website_persistence.py`) that verifies:
- ✅ The `user_id` column exists in the websites table
- ✅ Websites can be inserted with `user_id`
- ✅ Websites are saved with the correct `user_id`
- ✅ Websites can be filtered by `user_id`
- ✅ Database commits are working properly

All tests passed successfully.

## Impact

### Fixed Issues:
1. ✅ Websites now persist after refresh/reload
2. ✅ Each user only sees their own websites
3. ✅ Users cannot access, modify, or delete other users' websites
4. ✅ Proper user isolation and data security

### Security Improvements:
- All website-related endpoints now properly filter by `user_id`
- Users can only perform operations on their own websites
- Prevents unauthorized access to other users' data

## Deployment Notes

- No database migration required (the `user_id` column already exists with a default value)
- Existing websites in the database will have `user_id = 1` (default)
- New websites will be properly associated with the logged-in user
- The fix is backward compatible

## Date
October 10, 2025
