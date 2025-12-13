# save as rr_scraper.py
import time
import requests
from bs4 import BeautifulSoup
import re
import json

HEADERS = {"User-Agent": "detektive-rr-scraper/0.1 (hydrafore@gmail.com)"}
BASE = "https://www.royalroad.com"

def fetch_listing_page(page_num):
    url = f"{BASE}/fictions/best-rated?page={page_num}"
    r = requests.get(url, headers=HEADERS, timeout=15)
    r.raise_for_status()
    return r.text

def parse_listing_for_links(html):
    soup = BeautifulSoup(html, "html.parser")
    # selector may change; inspect RR pages. this looks for links in the list
    links = []
    for h2 in soup.select("h2.fiction-title"):
        a = h2.find("a")  # Find the <a> tag inside the <h2>
        if a:
            href = a.get("href")
            print(f"Found link: {href}")
            if href and href.startswith("/fiction/"):
                links.append(BASE + href)
    return links

def fetch_fiction_page(url):
    r = requests.get(url, headers=HEADERS, timeout=15)
    r.raise_for_status()
    return r.text

def parse_fiction_page(html):
    soup = BeautifulSoup(html, "html.parser")
    data = {}
    
    # title - Royal Road uses h1.font-white for fiction titles
    title_tag = soup.select_one("h1.font-white") or soup.select_one("h1.fiction-title") or soup.select_one("h1")
    data['title'] = title_tag.get_text(strip=True) if title_tag else None

    # author - Royal Road uses h4.font-white a for author links
    auth = soup.select_one("h4.font-white a")
    data['author'] = auth.get_text(strip=True) if auth else None

    # summary/description - Royal Road uses div.description
    summ = soup.select_one("div.description")
    data['summary'] = summ.get_text(strip=True) if summ else None

    # tags - Royal Road uses span.tags a.fiction-tag
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
    
    # fallback: try to read json data embedded (fixed deprecated 'text' parameter)
    script = soup.find("script", string=re.compile("window.__INITIAL_STATE__"))
    if script:
        m = re.search(r"window\.__INITIAL_STATE__\s*=\s*(\{.*\});", script.string, re.S)
        if m:
            try:
                j = json.loads(m.group(1))
                # inspect j to pull useful fields (example)
                data['raw_initial_state'] = True
            except Exception:
                pass

    return data

if __name__ == "__main__":
    # pilot: fetch first page and scrape first 3 links (reduced for testing)
    listing_html = fetch_listing_page(1)
    links = parse_listing_for_links(listing_html)
    print(f"Found {len(links)} links on page 1; sampling first 3...")
    for l in links[:3]:
        print("-" * 80)
        print("->", l)
        try:
            time.sleep(1.2)  # be polite
            fh = fetch_fiction_page(l)
            meta = parse_fiction_page(fh)
            print(json.dumps(meta, indent=2, ensure_ascii=False))
        except Exception as e:
            print("error scraping", l, e)
