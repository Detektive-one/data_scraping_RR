"""
Main orchestration script for Royal Road scraper.
Coordinates the entire scraping pipeline with checkpoint support.
"""
import signal
import sys
from db import init_db, get_session
from scraper import fetch_listing_page, fetch_fiction_page
from parser import parse_listing_links, parse_fiction_page
from normalizer import normalize_fiction
from loader import upsert_fictions
from checkpoint import Checkpoint
from utils import sleep_with_jitter, format_number, estimate_time_remaining
from config import (
    RATE_LIMIT_BETWEEN_PAGES,
    RATE_LIMIT_BETWEEN_FICTIONS,
    JITTER_PAGES,
    JITTER_FICTIONS,
    MAX_PAGES,
    MAX_NOVELS
)


# Global flag for graceful shutdown
shutdown_requested = False


def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully"""
    global shutdown_requested
    print("\n\n⚠ Interrupt received! Finishing current batch and saving checkpoint...")
    print("   Press Ctrl+C again to force quit (progress may be lost)")
    shutdown_requested = True


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
    """Main scraping loop with checkpoint support"""
    global shutdown_requested
    
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    print("=" * 80)
    print("Royal Road Scraper - Starting")
    print("=" * 80)
    print(f"Max pages: {MAX_PAGES:,}")
    print(f"Max novels: {MAX_NOVELS:,}")
    print(f"Rate limits: {RATE_LIMIT_BETWEEN_PAGES}s ±{JITTER_PAGES}s (pages), "
          f"{RATE_LIMIT_BETWEEN_FICTIONS}s ±{JITTER_FICTIONS}s (fictions)")
    print("=" * 80)
    
    # Initialize database
    init_db()
    session = get_session()
    
    # Load or create checkpoint
    checkpoint = Checkpoint()
    start_page = checkpoint.get_start_page()
    total_scraped = checkpoint.get_total_scraped()
    
    if start_page > 1:
        print(f"\n✓ Resuming from page {start_page} ({total_scraped:,} novels already scraped)")
        print(f"  Press Ctrl+C to pause and save progress\n")
    else:
        print(f"\n✓ Starting fresh scrape")
        print(f"  Press Ctrl+C to pause and save progress\n")
    
    try:
        for page in range(start_page, MAX_PAGES + 1):
            # Check if we've hit the hard cap
            if total_scraped >= MAX_NOVELS:
                print(f"\n✓ Reached maximum novel limit ({MAX_NOVELS:,}). Stopping.")
                break
            
            # Check for shutdown request
            if shutdown_requested:
                print(f"\n⚠ Shutdown requested. Saving checkpoint...")
                checkpoint.save(page, total_scraped)
                break
            
            novels_remaining = MAX_NOVELS - total_scraped
            time_est = estimate_time_remaining(novels_remaining)
            
            print(f"\n[Page {page}/{MAX_PAGES}] Fetching listing page... "
                  f"({format_number(total_scraped)}/{format_number(MAX_NOVELS)} novels, "
                  f"~{time_est} remaining)")
            
            try:
                # Fetch and parse listing page
                listing_html = fetch_listing_page(page)
                links = parse_listing_links(listing_html)
                
                if not links:
                    print(f"  No links found on page {page}. Stopping.")
                    break
                
                print(f"  Found {len(links)} fiction links")
                
                batch = []
                last_fiction_id = None
                
                # Scrape each fiction on this page
                for idx, link in enumerate(links, 1):
                    # Check hard cap before each fiction
                    if total_scraped >= MAX_NOVELS:
                        print(f"  ✓ Reached maximum novel limit ({MAX_NOVELS:,})")
                        break
                    
                    # Check for shutdown request
                    if shutdown_requested:
                        break
                    
                    try:
                        fiction_id = extract_fiction_id(link)
                        print(f"  [{idx}/{len(links)}] Scraping fiction {fiction_id}...", end=" ")
                        
                        # Fetch and parse fiction page
                        fiction_html = fetch_fiction_page(link)
                        raw = parse_fiction_page(fiction_html)
                        
                        # Add fiction ID
                        raw["fiction_id"] = fiction_id
                        
                        # Normalize and add to batch
                        normalized = normalize_fiction(raw)
                        batch.append(normalized)
                        last_fiction_id = fiction_id
                        
                        print(f"✓ {raw.get('title', 'Unknown')[:40]}")
                        
                        # Rate limiting with jitter between fictions
                        sleep_with_jitter(RATE_LIMIT_BETWEEN_FICTIONS, JITTER_FICTIONS)
                        
                    except Exception as e:
                        print(f"✗ ERROR: {e}")
                        continue
                
                # Insert batch into database
                if batch:
                    upsert_fictions(session, batch)
                    total_scraped += len(batch)
                    print(f"  ✓ Inserted {len(batch)} records (Total: {format_number(total_scraped)})")
                    
                    # Save checkpoint after each successful page
                    checkpoint.save(page + 1, total_scraped, last_fiction_id)
                
                # Check if we should stop
                if shutdown_requested or total_scraped >= MAX_NOVELS:
                    break
                
                # Rate limiting with jitter between listing pages
                print(f"  Sleeping {RATE_LIMIT_BETWEEN_PAGES}s ±{JITTER_PAGES}s...")
                sleep_with_jitter(RATE_LIMIT_BETWEEN_PAGES, JITTER_PAGES)
                
            except Exception as e:
                print(f"  ERROR on page {page}: {e}")
                # Save checkpoint even on error
                checkpoint.save(page, total_scraped)
                continue
    
    except KeyboardInterrupt:
        print("\n\n⚠ Force quit detected!")
        checkpoint.save(page, total_scraped)
    
    finally:
        session.close()
        print("\n" + "=" * 80)
        print(f"Scraping {'paused' if shutdown_requested else 'complete'}!")
        print(f"Total records: {format_number(total_scraped)}")
        print(f"Last page: {page}")
        if shutdown_requested:
            print(f"\n✓ Progress saved. Run again to resume from page {page}")
        print("=" * 80)


if __name__ == "__main__":
    main()
