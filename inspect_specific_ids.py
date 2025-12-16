import requests
from bs4 import BeautifulSoup

def inspect_ids(ids):
    print("Inspecting specific IDs for missed status...")
    for fid in ids:
        url = f"https://www.royalroad.com/fiction/{fid}"
        try:
            r = requests.get(url, headers={'User-Agent': 'detektive-rr-scraper/0.1'})
            soup = BeautifulSoup(r.text, 'html.parser')
            print(f"\nID {fid}: {soup.select_one('h1').get_text(strip=True)}")
            
            # Print all labels to see what we're missing
            labels = soup.select('.fiction-info .label')
            for l in labels:
                print(f"  - '{l.get_text(strip=True)}'")
        except Exception as e:
            print(f"Error fetching {fid}: {e}")

if __name__ == "__main__":
    inspect_ids([25, 29, 31, 32, 33])
