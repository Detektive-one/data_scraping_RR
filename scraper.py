"""
HTTP fetching functions for Royal Road scraper.
Handles all network requests with proper headers and rate limiting.
"""
import requests
from config import BASE_URL, HEADERS, TIMEOUT


def fetch_listing_page(page_num):
    """
    Fetch a listing page from Royal Road's best-rated section.
    
    Args:
        page_num (int): Page number to fetch (1-indexed)
        
    Returns:
        str: HTML content of the listing page
        
    Raises:
        requests.HTTPError: If the request fails
    """
    url = f"{BASE_URL}/fictions/best-rated?page={page_num}"
    r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    r.raise_for_status()
    return r.text


def fetch_fiction_page(url):
    """
    Fetch a specific fiction page.
    
    Args:
        url (str): Full URL to the fiction page
        
    Returns:
        str: HTML content of the fiction page
        
    Raises:
        requests.HTTPError: If the request fails
    """
    r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    r.raise_for_status()
    return r.text
