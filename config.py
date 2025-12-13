# Configuration constants for Royal Road scraper

# Base URL and headers
BASE_URL = "https://www.royalroad.com"
HEADERS = {
    "User-Agent": "detektive-rr-scraper/0.1 (hydrafore@gmail.com)"
}

# Rate limiting (in seconds)
RATE_LIMIT_BETWEEN_PAGES = 1.5  # Between listing pages
RATE_LIMIT_BETWEEN_FICTIONS = 0.5  # Between individual fiction pages

# Jitter settings (anti-fingerprinting)
JITTER_PAGES = 0.3  # Random jitter for page delays (0 to 0.3s)
JITTER_FICTIONS = 0.2  # Random jitter for fiction delays (0 to 0.2s)

# Scraping limits
MAX_PAGES = 3000  # Maximum listing pages to scrape (~60k novels)
MAX_NOVELS = 65000  # Hard cap on total novels to scrape
TIMEOUT = 15  # HTTP request timeout in seconds

# Checkpoint system
CHECKPOINT_FILE = "scraper_checkpoint.json"  # File to save progress

# Database
DB_PATH = "sqlite:///royalroad.db"
