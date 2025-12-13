# Royal Road Fiction Scraper

A modular web scraper for collecting fiction metadata from RoyalRoad.com.

## Project Structure

```
data_scraping_RR/
│
├── config.py          # Configuration constants (URLs, rate limits, etc.)
├── db.py              # SQLAlchemy engine, session, and Fiction model
├── scraper.py         # HTTP fetching functions
├── parser.py          # HTML parsing functions
├── normalizer.py      # Data cleanup and type conversion
├── loader.py          # Database insert/upsert operations
├── run_scrape.py      # Main orchestration script
├── simple_scrapper.py # Original prototype (for reference)
└── royalroad.db       # SQLite database (created on first run)
```

## Pipeline Flow

```
fetch_listing_page(page_n)
        ↓
parse_listing_links()
        ↓
fetch_fiction_page(link)
        ↓
parse_fiction_data()
        ↓
normalize_data()
        ↓
upsert_batch_into_sqlite()
        ↓
sleep()
```

## Installation

1. Install required dependencies:
```bash
pip install requests beautifulsoup4 sqlalchemy
```

## Usage

### Run the full scraper:
```bash
python run_scrape.py
```

This will:
- Initialize the SQLite database
- Scrape fiction listings from Royal Road's best-rated section
- Extract metadata for each fiction
- Store data in the database with automatic deduplication

### Configuration

Edit `config.py` to adjust:
- `MAX_PAGES`: Number of listing pages to scrape (default: 3000)
- `RATE_LIMIT_BETWEEN_PAGES`: Delay between listing pages (default: 1.5s)
- `RATE_LIMIT_BETWEEN_FICTIONS`: Delay between fiction pages (default: 0.5s)

## Database Schema

The `fictions` table contains:

| Column        | Type    | Description                    |
|---------------|---------|--------------------------------|
| fiction_id    | Integer | Primary key (from URL)         |
| title         | String  | Fiction title                  |
| author        | String  | Author name                    |
| tags          | Text    | JSON array of genre tags       |
| pages         | Integer | Number of pages                |
| views         | Integer | Total view count               |
| avg_views     | Integer | Average views per chapter      |
| followers     | Integer | Follower count                 |
| favorites     | Integer | Favorite count                 |
| rating_count  | Integer | Number of ratings              |
| avg_rating    | Float   | Average rating (0-5)           |
| status        | String  | Publication status             |
| last_updated  | String  | Last update date               |
| scraped_at    | String  | ISO timestamp of scrape        |

## Features

- ✅ Modular architecture with clear separation of concerns
- ✅ Automatic database initialization
- ✅ Upsert logic (updates existing records)
- ✅ Rate limiting to be respectful to the server
- ✅ Error handling and retry logic
- ✅ Progress reporting
- ✅ Graceful shutdown on Ctrl+C

## Notes

- The scraper uses Royal Road's best-rated listing as the source
- Rate limits are conservative to avoid overwhelming the server
- Fiction IDs are extracted from URLs and used as primary keys
- Tags are stored as JSON strings for easy querying
