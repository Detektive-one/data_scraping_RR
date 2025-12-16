"""
Inspect ALL labels on fictions to identify missed status types.
"""
import requests
from bs4 import BeautifulSoup

def inspect_labels(fiction_id):
    url = f"https://www.royalroad.com/fiction/{fiction_id}"
    print(f"\nChecking ID: {fiction_id} ({url})")
    try:
        r = requests.get(url, headers={'User-Agent': 'detektive-rr-scraper/0.1'})
        soup = BeautifulSoup(r.text, 'html.parser')
        
        title = soup.select_one('h1').get_text(strip=True) if soup.select_one('h1') else "Unknown"
        print(f"Title: {title}")
        
        labels = soup.select('.fiction-info .label')
        print("Labels found:")
        for l in labels:
            print(f"  - '{l.get_text(strip=True)}' (Classes: {l.get('class')})")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Test a mix of IDs, hoping to catch Hiatus/Dropped/Inactive
    # You can add the specific ID you saw issues with here
    test_ids = [21220, 3, 22, 25, 59, 100, 1000] 
    
    for fid in test_ids:
        inspect_labels(fid)
