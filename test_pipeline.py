"""
Test script to verify the scraper pipeline works correctly.
Tests each component individually and then the full pipeline.
"""
import json
from db import init_db, get_session
from scraper import fetch_listing_page, fetch_fiction_page
from parser import parse_listing_links, parse_fiction_page
from normalizer import normalize_fiction
from loader import upsert_fictions


def test_listing_scrape():
    """Test fetching and parsing a listing page"""
    print("\n" + "=" * 80)
    print("TEST 1: Listing Page Scrape")
    print("=" * 80)
    
    html = fetch_listing_page(1)
    links = parse_listing_links(html)
    
    print(f"✓ Fetched listing page 1")
    print(f"✓ Found {len(links)} fiction links")
    print(f"  Sample links:")
    for link in links[:3]:
        print(f"    - {link}")
    
    return links


def test_fiction_scrape(url):
    """Test fetching and parsing a fiction page"""
    print("\n" + "=" * 80)
    print("TEST 2: Fiction Page Scrape")
    print("=" * 80)
    print(f"Testing with: {url}")
    
    html = fetch_fiction_page(url)
    data = parse_fiction_page(html)
    
    print(f"\n✓ Fetched fiction page")
    print(f"✓ Parsed fiction data:")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    
    return data


def test_normalization(raw_data, fiction_id):
    """Test data normalization"""
    print("\n" + "=" * 80)
    print("TEST 3: Data Normalization")
    print("=" * 80)
    
    raw_data["fiction_id"] = fiction_id
    normalized = normalize_fiction(raw_data)
    
    print(f"✓ Normalized data:")
    print(json.dumps(normalized, indent=2, ensure_ascii=False, default=str))
    
    return normalized


def test_database_insert(normalized_data):
    """Test database insertion"""
    print("\n" + "=" * 80)
    print("TEST 4: Database Insertion")
    print("=" * 80)
    
    init_db()
    session = get_session()
    
    try:
        upsert_fictions(session, [normalized_data])
        print(f"✓ Inserted record into database")
        
        # Verify insertion
        from db import Fiction
        record = session.query(Fiction).filter_by(
            fiction_id=normalized_data["fiction_id"]
        ).first()
        
        if record:
            print(f"✓ Verified record in database:")
            print(f"  - ID: {record.fiction_id}")
            print(f"  - Title: {record.title}")
            print(f"  - Author: {record.author}")
            print(f"  - Views: {record.views:,}" if record.views else "  - Views: None")
            print(f"  - Rating: {record.avg_rating}" if record.avg_rating else "  - Rating: None")
        else:
            print("✗ Record not found in database!")
            
    finally:
        session.close()


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("ROYAL ROAD SCRAPER - PIPELINE TEST")
    print("=" * 80)
    
    try:
        # Test 1: Fetch listing page
        links = test_listing_scrape()
        
        if not links:
            print("\n✗ No links found. Cannot continue tests.")
            return
        
        # Test 2: Fetch fiction page
        test_url = links[0]
        fiction_id = int(test_url.split("/")[4])
        raw_data = test_fiction_scrape(test_url)
        
        # Test 3: Normalize data
        normalized = test_normalization(raw_data, fiction_id)
        
        # Test 4: Insert into database
        test_database_insert(normalized)
        
        print("\n" + "=" * 80)
        print("✓ ALL TESTS PASSED!")
        print("=" * 80)
        print("\nThe scraper pipeline is working correctly.")
        print("You can now run: python run_scrape.py")
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
