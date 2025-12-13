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
├── checkpoint.py      # Checkpoint management for pause/resume
├── utils.py           # Utility functions (jitter, formatting)
├── run_scrape.py      # Main orchestration script
├── manage_checkpoint.py  # Checkpoint management utility
├── test_pipeline.py   # Test suite
├── simple_scrapper.py # Original prototype (for reference)
├── scraper_checkpoint.json  # Progress checkpoint (auto-created)
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
- ✅ **Checkpoint system** - Pause and resume scraping anytime
- ✅ **Jitter-based rate limiting** - Anti-fingerprinting timing randomization
- ✅ **Hard cap on novels** - Stops automatically at 65,000 novels
- ✅ Error handling and retry logic
- ✅ Progress reporting with time estimates
- ✅ Graceful shutdown on Ctrl+C

## Usage

### Basic Scraping

```bash
# Start scraping (or resume from checkpoint)
python run_scrape.py
```

### Pause and Resume

**To pause:**
- Press `Ctrl+C` once - the scraper will finish the current batch and save progress
- Press `Ctrl+C` twice - force quit (may lose current batch)

**To resume:**
- Simply run `python run_scrape.py` again - it will automatically resume from the last checkpoint

### Manage Checkpoints

```bash
# View current checkpoint status
python manage_checkpoint.py show

# Clear checkpoint to start fresh
python manage_checkpoint.py clear

# Interactive menu
python manage_checkpoint.py
```

### Configuration

Edit `config.py` to adjust:

- **MAX_PAGES**: Number of listing pages (default: 3000)
- **MAX_NOVELS**: Hard cap on total novels (default: 65,000)
- **RATE_LIMIT_BETWEEN_PAGES**: Base delay between pages (default: 1.5s)
- **RATE_LIMIT_BETWEEN_FICTIONS**: Base delay between fictions (default: 0.5s)
- **JITTER_PAGES**: Random jitter for pages (default: 0.3s)
- **JITTER_FICTIONS**: Random jitter for fictions (default: 0.2s)

## How It Works

### Checkpoint System

The scraper automatically saves progress after each page:
- **Current page number** - Where to resume from
- **Total novels scraped** - Running count
- **Last fiction ID** - For verification
- **Timestamp** - When checkpoint was saved

Checkpoint is saved to `scraper_checkpoint.json`

### Anti-Fingerprinting

Rate limiting uses **jitter** (random delays) to avoid robotic timing:
```python
# Instead of always sleeping 1.5s
sleep(1.5)

# We sleep 1.5s + random(0 to 0.3s)
sleep_with_jitter(1.5, 0.3)  # Sleeps 1.5-1.8s
```

This makes request timing appear more human-like.

### Hard Cap

The scraper will automatically stop when:
1. **MAX_NOVELS** (65,000) is reached, OR
2. **MAX_PAGES** (3000) is reached, OR
3. No more fictions are found

## Notes

- The scraper uses Royal Road's best-rated listing as the source
- Rate limits are conservative to avoid overwhelming the server
- Fiction IDs are extracted from URLs and used as primary keys
- Tags are stored as JSON strings for easy querying
