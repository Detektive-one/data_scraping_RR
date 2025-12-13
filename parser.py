"""
HTML parsing functions for Royal Road scraper.
Extracts structured data from Royal Road HTML pages.
"""
import re
import json
from bs4 import BeautifulSoup
from config import BASE_URL


def parse_listing_links(html):
    """
    Parse fiction links from a listing page.
    
    Args:
        html (str): HTML content of a listing page
        
    Returns:
        list: List of full URLs to fiction pages
    """
    soup = BeautifulSoup(html, "html.parser")
    links = []
    
    for h2 in soup.select("h2.fiction-title"):
        a = h2.find("a")  # Find the <a> tag inside the <h2>
        if a:
            href = a.get("href")
            if href and href.startswith("/fiction/"):
                links.append(BASE_URL + href)
    
    return links


def parse_fiction_page(html):
    """
    Parse fiction metadata from a fiction page.
    
    Args:
        html (str): HTML content of a fiction page
        
    Returns:
        dict: Dictionary containing fiction metadata with keys:
            - title (str)
            - author (str)
            - summary (str)
            - tags (list)
            - views (str)
            - avg_views (str)
            - followers (str)
            - favorites (str)
            - rating_count (str)
            - pages (str)
            - avg_rating (str)
            - status (str or None)
            - last_updated (str or None)
    """
    soup = BeautifulSoup(html, "html.parser")
    data = {}
    
    # Title - Royal Road uses h1.font-white for fiction titles
    title_tag = soup.select_one("h1.font-white") or soup.select_one("h1.fiction-title") or soup.select_one("h1")
    data['title'] = title_tag.get_text(strip=True) if title_tag else None

    # Author - Royal Road uses h4.font-white a for author links
    auth = soup.select_one("h4.font-white a")
    data['author'] = auth.get_text(strip=True) if auth else None

    # Summary/description - Royal Road uses div.description
    summ = soup.select_one("div.description")
    data['summary'] = summ.get_text(strip=True) if summ else None

    # Tags - Royal Road uses span.tags a.fiction-tag
    tags = [t.get_text(strip=True) for t in soup.select("span.tags a.fiction-tag")]
    data['tags'] = tags

    # Stats are in .stats-content .list-unstyled li elements
    # They come in pairs: label li, then value li
    stats_items = soup.select('.stats-content .list-unstyled li')
    stats_dict = {}
    
    # Parse stats - they alternate between label and value
    i = 0
    while i < len(stats_items):
        label_text = stats_items[i].get_text(strip=True)
        # If next item exists and current item looks like a label (ends with :)
        if ':' in label_text and i + 1 < len(stats_items):
            key = label_text.replace(':', '').strip()
            value = stats_items[i + 1].get_text(strip=True)
            stats_dict[key] = value
            i += 2
        else:
            i += 1
    
    # Extract specific stats
    data['views'] = stats_dict.get('Total Views') or stats_dict.get('Views')
    data['avg_views'] = stats_dict.get('Average Views')
    data['followers'] = stats_dict.get('Followers')
    data['favorites'] = stats_dict.get('Favorites')
    data['rating_count'] = stats_dict.get('Ratings')
    data['pages'] = stats_dict.get('Pages')
    
    # Try to get rating from meta tag
    rating_meta = soup.select_one('meta[property="books:rating:value"]')
    data['avg_rating'] = rating_meta.get('content') if rating_meta else None
    
    # Status and last updated (if available)
    data['status'] = stats_dict.get('Status')
    data['last_updated'] = stats_dict.get('Last Updated')

    return data
