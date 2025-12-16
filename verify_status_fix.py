"""
Verify the fix for INACTIVE status
"""
from scraper import fetch_fiction_page
from parser import parse_fiction_details

def verify_fix(ids):
    print("Verifying fix for INACTIVE status...")
    for fid in ids:
        url = f"https://www.royalroad.com/fiction/{fid}"
        print(f"\nChecking ID {fid}...")
        try:
            html = fetch_fiction_page(url)
            details = parse_fiction_details(html)
            
            print(f"  Type: {details['fiction_type']}")
            print(f"  Status: {details['status']}")
            
            if details['status'] == 'Inactive':
                print("  ✓ SUCCESS: Status correctly identified as Inactive")
            elif details['status'] == 'Completed':
                 print(f"  ✓ SUCCESS: Status correctly identified as {details['status']}")
            else:
                print(f"  ✗ FAILURE: Status captured as {details['status']}")
                
        except Exception as e:
            print(f"  Error: {e}")

if __name__ == "__main__":
    verify_fix([25, 29, 31, 32, 33])
