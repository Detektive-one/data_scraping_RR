"""
Script to update existing fictions in the database with missing fields.
Adds: fiction_type, warn_tags, content_warnings, and fixes status/last_updated.
"""
import time
import json
import os
import signal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db import Fiction, get_session
from scraper import fetch_fiction_page
from parser import parse_fiction_details
from utils import sleep_with_jitter, format_number, estimate_time_remaining
from config import RATE_LIMIT_BETWEEN_FICTIONS, JITTER_FICTIONS

# Constants
CHECKPOINT_FILE = "update_checkpoint.json"
UPDATE_BATCH_SIZE = 50

# Global shutdown flag
shutdown_requested = False

def signal_handler(signum, frame):
    """Handle Ctrl+C"""
    global shutdown_requested
    print("\n\n⚠ Interrupt received! Finishing current batch and saving progress...")
    shutdown_requested = True

def load_checkpoint():
    """Load the last processed fiction ID"""
    if os.path.exists(CHECKPOINT_FILE):
        try:
            with open(CHECKPOINT_FILE, 'r') as f:
                data = json.load(f)
                id_val = data.get('last_processed_id', 0)
                print(f"✓ Resuming from fiction ID > {id_val}")
                return id_val
        except:
            pass
    return 0

def save_checkpoint(last_id):
    """Save the last processed fiction ID"""
    with open(CHECKPOINT_FILE, 'w') as f:
        json.dump({'last_processed_id': last_id, 'timestamp': time.time()}, f)

def main():
    global shutdown_requested
    signal.signal(signal.SIGINT, signal_handler)
    
    print("=" * 80)
    print("Royal Road Database Updater")
    print("Adding: fiction_type, warnings, status, last_updated")
    print("=" * 80)

    session = get_session()
    
    try:
        last_id = load_checkpoint()
        
        # Get count of fictions to update
        total_count = session.query(Fiction).count()
        remaining_count = session.query(Fiction).filter(Fiction.fiction_id > last_id).count()
        
        print(f"Total fictions in DB: {format_number(total_count)}")
        print(f"Remaining to update: {format_number(remaining_count)}")
        print(f"Est. time: {estimate_time_remaining(remaining_count, RATE_LIMIT_BETWEEN_FICTIONS + JITTER_FICTIONS/2)}")
        print("-" * 80)
        
        # Fetch fictions in batches
        # We query for IDs > last_id, ordered by ID
        query = session.query(Fiction).filter(Fiction.fiction_id > last_id).order_by(Fiction.fiction_id)
        
        updated_count = 0
        
        # Iterate through the query result
        # Note: loading all at once might be heavy if db is huge, but with 65k it's ~few MBs, acceptable.
        # Ideally use yield_per or paging. Let's use simple paging.
        
        offset = 0
        while not shutdown_requested:
            # Get next batch
            batch = query.limit(UPDATE_BATCH_SIZE).offset(offset).all()
            
            if not batch:
                break
                
            # If we used offset with the same query object, we'd need to assume the underlying data doesn't change order.
            # actually better to just fetch relative to the last_id dynamically
            # But since we are iterating, let's just use the query generator if possible or manual batches
            # Let's simple iterate the cursor
            pass 
            
            # Re-querying is cleaner for simple batching logic
            batch = session.query(Fiction).filter(Fiction.fiction_id > last_id).order_by(Fiction.fiction_id).limit(UPDATE_BATCH_SIZE).all()
            
            if not batch:
                break

            for fiction in batch:
                if shutdown_requested:
                    break
                    
                print(f"[{updated_count + 1}] Updating {fiction.title[:30]} (ID: {fiction.fiction_id})...", end=" ")
                
                try:
                    # Construct URL
                    url = f"https://www.royalroad.com/fiction/{fiction.fiction_id}"
                    
                    # Fetch page
                    html = fetch_fiction_page(url)
                    
                    # Parse details
                    details = parse_fiction_details(html)
                    
                    # Update fields
                    if details['fiction_type']:
                        fiction.fiction_type = details['fiction_type']
                    if details['status']:
                        fiction.status = details['status']
                    if details['last_updated']:
                        fiction.last_updated = details['last_updated']
                    
                    # Store lists as JSON strings
                    if details['warning_tags']:
                        fiction.warn_tags = json.dumps(details['warning_tags'], ensure_ascii=False)
                    else:
                        fiction.warn_tags = "[]"
                        
                    if details['content_warnings']:
                        fiction.content_warnings = json.dumps(details['content_warnings'], ensure_ascii=False)
                    else:
                        fiction.content_warnings = "[]"
                        
                    print("✓ Done")
                    
                    # Update loop vars
                    last_id = fiction.fiction_id
                    updated_count += 1
                    
                    # Rate limit
                    sleep_with_jitter(RATE_LIMIT_BETWEEN_FICTIONS, JITTER_FICTIONS)
                    
                except Exception as e:
                    print(f"✗ Error: {e}")
                    # Skip on error but advance last_id to avoid stuck loop
                    last_id = fiction.fiction_id
            
            # Commit processing of the batch
            session.commit()
            save_checkpoint(last_id)
            
            # If batch was empty or finished, loop condition handles it
            
    except Exception as e:
        print(f"\n✗ Critical Error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        session.close()
        print("\n" + "=" * 80)
        print("Update Process Finished")
        print(f"Total updated this session: {updated_count}")
        print("=" * 80)

if __name__ == "__main__":
    main()
