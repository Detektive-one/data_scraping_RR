"""
Data normalization and type conversion functions.
Converts raw scraped data into database-ready format.
"""
import json
from datetime import datetime


def to_int(val):
    """
    Convert a string with commas to integer.
    
    Args:
        val (str): String like "24,822,333"
        
    Returns:
        int or None: Integer value or None if conversion fails
    """
    if not val:
        return None
    try:
        return int(val.replace(",", ""))
    except (ValueError, AttributeError):
        return None


def to_float(val):
    """
    Convert a string to float.
    
    Args:
        val (str): String like "4.83213"
        
    Returns:
        float or None: Float value or None if conversion fails
    """
    if not val:
        return None
    try:
        return float(val)
    except (ValueError, AttributeError):
        return None


def normalize_fiction(raw):
    """
    Normalize raw fiction data into database-ready format.
    
    Args:
        raw (dict): Raw fiction data from parser with fiction_id added
        
    Returns:
        dict: Normalized data ready for database insertion
    """
    return {
        "fiction_id": raw["fiction_id"],
        "title": raw["title"].strip() if raw.get("title") else None,
        "author": raw["author"].strip() if raw.get("author") else None,

        "tags": json.dumps(raw.get("tags", []), ensure_ascii=False),
        "pages": to_int(raw.get("pages")),

        "views": to_int(raw.get("views")),
        "avg_views": to_int(raw.get("avg_views")),
        "followers": to_int(raw.get("followers")),
        "favorites": to_int(raw.get("favorites")),
        "rating_count": to_int(raw.get("rating_count")),
        "avg_rating": to_float(raw.get("avg_rating")),

        "status": raw.get("status"),
        "last_updated": raw.get("last_updated"),

        "scraped_at": datetime.utcnow().isoformat()
    }
