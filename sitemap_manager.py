"""
Sitemap Manager - Storage and management for website sitemaps
"""

import json
import os
from datetime import datetime
import uuid
from backend_utils import fetch_sitemap_urls, find_sitemap

STORAGE_FILE = 'sitemap_storage.json'

def load_storage():
    """Load sitemap storage from JSON file"""
    if not os.path.exists(STORAGE_FILE):
        return {"websites": []}
    
    try:
        with open(STORAGE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading storage: {e}")
        return {"websites": []}

def save_storage(data):
    """Save sitemap storage to JSON file"""
    try:
        with open(STORAGE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving storage: {e}")
        return False

def save_sitemap(website_url, sitemap_url, urls):
    """
    Save or update sitemap data for a website
    
    Args:
        website_url: Base URL of the website
        sitemap_url: URL of the sitemap
        urls: List of URL dictionaries
    
    Returns:
        dict: {"success": bool, "id": str, "message": str}
    """
    try:
        storage = load_storage()
        
        # Check if website already exists
        existing = None
        for site in storage["websites"]:
            if site["website_url"] == website_url:
                existing = site
                break
        
        if existing:
            # Update existing
            existing["sitemap_url"] = sitemap_url
            existing["urls"] = urls
            existing["total_count"] = len(urls)
            existing["last_updated"] = datetime.now().isoformat()
            existing["status"] = "success"
            site_id = existing["id"]
            message = "Sitemap updated successfully"
        else:
            # Create new
            site_id = str(uuid.uuid4())
            new_site = {
                "id": site_id,
                "website_url": website_url,
                "sitemap_url": sitemap_url,
                "urls": urls,
                "total_count": len(urls),
                "last_updated": datetime.now().isoformat(),
                "status": "success"
            }
            storage["websites"].append(new_site)
            message = "Sitemap saved successfully"
        
        if save_storage(storage):
            return {
                "success": True,
                "id": site_id,
                "message": message,
                "total_count": len(urls)
            }
        else:
            return {
                "success": False,
                "error": "Failed to save storage"
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Error saving sitemap: {str(e)}"
        }

def get_all_sitemaps():
    """Get all saved sitemaps"""
    storage = load_storage()
    return {
        "success": True,
        "websites": storage["websites"]
    }

def get_sitemap_by_id(site_id):
    """Get a specific sitemap by ID"""
    storage = load_storage()
    for site in storage["websites"]:
        if site["id"] == site_id:
            return {
                "success": True,
                "website": site
            }
    return {
        "success": False,
        "error": "Sitemap not found"
    }

def refresh_sitemap(site_id):
    """
    Refresh a sitemap by fetching new URLs
    
    Args:
        site_id: ID of the website to refresh
    
    Returns:
        dict: {"success": bool, "message": str, "total_count": int}
    """
    try:
        storage = load_storage()
        site = None
        
        for s in storage["websites"]:
            if s["id"] == site_id:
                site = s
                break
        
        if not site:
            return {
                "success": False,
                "error": "Sitemap not found"
            }
        
        # Fetch new URLs
        print(f"🔄 Refreshing sitemap for {site['website_url']}")
        urls = fetch_sitemap_urls(site["sitemap_url"])
        
        if not urls:
            site["status"] = "error"
            site["last_updated"] = datetime.now().isoformat()
            save_storage(storage)
            return {
                "success": False,
                "error": "No URLs found in sitemap"
            }
        
        # Update site data
        site["urls"] = urls
        site["total_count"] = len(urls)
        site["last_updated"] = datetime.now().isoformat()
        site["status"] = "success"
        
        if save_storage(storage):
            return {
                "success": True,
                "message": "Sitemap refreshed successfully",
                "total_count": len(urls)
            }
        else:
            return {
                "success": False,
                "error": "Failed to save updated sitemap"
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Error refreshing sitemap: {str(e)}"
        }

def delete_sitemap(site_id):
    """Delete a sitemap by ID"""
    try:
        storage = load_storage()
        original_count = len(storage["websites"])
        
        storage["websites"] = [s for s in storage["websites"] if s["id"] != site_id]
        
        if len(storage["websites"]) < original_count:
            if save_storage(storage):
                return {
                    "success": True,
                    "message": "Sitemap deleted successfully"
                }
        
        return {
            "success": False,
            "error": "Sitemap not found"
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Error deleting sitemap: {str(e)}"
        }

def refresh_all_sitemaps():
    """
    Refresh all saved sitemaps
    Used by scheduled task
    
    Returns:
        dict: {"success": bool, "results": list}
    """
    storage = load_storage()
    results = []
    
    for site in storage["websites"]:
        print(f"\n🔄 Refreshing {site['website_url']}...")
        result = refresh_sitemap(site["id"])
        results.append({
            "website_url": site["website_url"],
            "success": result["success"],
            "message": result.get("message") or result.get("error"),
            "total_count": result.get("total_count", 0)
        })
    
    return {
        "success": True,
        "results": results,
        "total_refreshed": len([r for r in results if r["success"]])
    }
