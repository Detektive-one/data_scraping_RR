"""
Main orchestration script for Royal Road scraper.
Coordinates the entire scraping pipeline.
"""
import time
from db import init_db, get_session
from scraper import fetch_listing_page, fetch_fiction_page
from parser import parse_listing_links, parse_fiction_page
from normalizer import normalize_fiction
from loader import upsert_fictions
from config import (
    RATE_LIMIT_BETWEEN_PAGES,
    RATE_LIMIT_BETWEEN_FICTIONS,
    MAX_PAGES
)


def extract_fiction_id(url):
    """
    Extract fiction ID from Royal Road URL.
    
    Args:
        url (str): URL like "https://www.royalroad.com/fiction/21220/mother-of-learning"
        
    Returns:
        int: Fiction ID
    """
    # URL format: /fiction/{id}/{slug}
    parts = url.split("/")
    return int(parts[4])


def main():
    """Main scraping loop"""
    print("=" * 80)
    print("Royal Road Scraper - Starting")
    print("=" * 80)
    
    # Initialize database
    init_db()
    session = get_session()
    
    total_scraped = 0
    
    try:
        for page in range(1, MAX_PAGES + 1):
            print(f"\n[Page {page}/{MAX_PAGES}] Fetching listing page...")
            
            try:
                # Fetch and parse listing page
                listing_html = fetch_listing_page(page)
                links = parse_listing_links(listing_html)
                
                if not links:
                    print(f"  No links found on page {page}. Stopping.")
                    break
                
                print(f"  Found {len(links)} fiction links")
                
                batch = []
                
                # Scrape each fiction on this page
                for idx, link in enumerate(links, 1):
                    try:
                        print(f"  [{idx}/{len(links)}] Scraping: {link}")
                        
                        # Fetch and parse fiction page
                        fiction_html = fetch_fiction_page(link)
                        raw = parse_fiction_page(fiction_html)
                        
                        # Add fiction ID
                        raw["fiction_id"] = extract_fiction_id(link)
                        
                        # Normalize and add to batch
                        normalized = normalize_fiction(raw)
                        batch.append(normalized)
                        
                        # Rate limiting between fictions
                        time.sleep(RATE_LIMIT_BETWEEN_FICTIONS)
                        
                    except Exception as e:
                        print(f"    ERROR scraping {link}: {e}")
                        continue
                
                # Insert batch into database
                if batch:
                    upsert_fictions(session, batch)
                    total_scraped += len(batch)
                    print(f"  ✓ Inserted {len(batch)} records (Total: {total_scraped})")
                
                # Rate limiting between listing pages
                print(f"  Sleeping for {RATE_LIMIT_BETWEEN_PAGES}s...")
                time.sleep(RATE_LIMIT_BETWEEN_PAGES)
                
            except Exception as e:
                print(f"  ERROR on page {page}: {e}")
                continue
    
    except KeyboardInterrupt:
        print("\n\nScraping interrupted by user.")
    
    finally:
        session.close()
        print("\n" + "=" * 80)
        print(f"Scraping complete! Total records: {total_scraped}")
        print("=" * 80)


if __name__ == "__main__":
    main()
