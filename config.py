# Configuration constants for Royal Road scraper

# Base URL and headers
BASE_URL = "https://www.royalroad.com"
HEADERS = {
    "User-Agent": "detektive-rr-scraper/0.1 (hydrafore@gmail.com)"
}

# Rate limiting (in seconds)
RATE_LIMIT_BETWEEN_PAGES = 1.5  # Between listing pages
RATE_LIMIT_BETWEEN_FICTIONS = 0.5  # Between individual fiction pages

# Scraping limits
MAX_PAGES = 3000  # Maximum listing pages to scrape (~60k novels)
TIMEOUT = 15  # HTTP request timeout in seconds

# Database
DB_PATH = "sqlite:///royalroad.db"
