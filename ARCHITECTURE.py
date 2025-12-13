"""
Royal Road Scraper - Architecture Overview
==========================================

This file provides a visual overview of how all components work together.
"""

# =============================================================================
# COMPONENT DIAGRAM
# =============================================================================

"""
┌─────────────────────────────────────────────────────────────────────┐
│                         run_scrape.py                                │
│                    (Main Orchestration)                              │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  for page in range(1, MAX_PAGES):                           │   │
│  │      1. Fetch listing page                                   │   │
│  │      2. Parse fiction links                                  │   │
│  │      3. For each link:                                       │   │
│  │         - Fetch fiction page                                 │   │
│  │         - Parse metadata                                     │   │
│  │         - Normalize data                                     │   │
│  │         - Add to batch                                       │   │
│  │      4. Upsert batch to database                             │   │
│  │      5. Sleep (rate limiting)                                │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              │ uses
                              ▼
        ┌─────────────────────────────────────────────────┐
        │                                                  │
        │  ┌──────────────┐      ┌──────────────┐        │
        │  │  scraper.py  │      │  parser.py   │        │
        │  │              │      │              │        │
        │  │ - fetch_     │      │ - parse_     │        │
        │  │   listing_   │      │   listing_   │        │
        │  │   page()     │      │   links()    │        │
        │  │              │      │              │        │
        │  │ - fetch_     │      │ - parse_     │        │
        │  │   fiction_   │      │   fiction_   │        │
        │  │   page()     │      │   page()     │        │
        │  └──────────────┘      └──────────────┘        │
        │                                                  │
        │  ┌──────────────┐      ┌──────────────┐        │
        │  │normalizer.py │      │  loader.py   │        │
        │  │              │      │              │        │
        │  │ - to_int()   │      │ - upsert_    │        │
        │  │ - to_float() │      │   fictions() │        │
        │  │ - normalize_ │      │              │        │
        │  │   fiction()  │      │ - insert_    │        │
        │  │              │      │   fictions() │        │
        │  └──────────────┘      └──────────────┘        │
        │                                                  │
        │  ┌──────────────┐      ┌──────────────┐        │
        │  │   db.py      │      │  config.py   │        │
        │  │              │      │              │        │
        │  │ - Fiction    │      │ - BASE_URL   │        │
        │  │   model      │      │ - HEADERS    │        │
        │  │ - engine     │      │ - RATE_      │        │
        │  │ - init_db()  │      │   LIMITS     │        │
        │  │              │      │ - MAX_PAGES  │        │
        │  └──────────────┘      └──────────────┘        │
        │                                                  │
        └─────────────────────────────────────────────────┘
"""

# =============================================================================
# DATA FLOW
# =============================================================================

"""
Royal Road Website
        │
        │ HTTP GET
        ▼
┌─────────────────┐
│ Listing Page    │ (HTML)
│ /best-rated?p=1 │
└─────────────────┘
        │
        │ parse_listing_links()
        ▼
┌─────────────────┐
│ Fiction URLs    │ (List)
│ [/fiction/123,  │
│  /fiction/456,  │
│  ...]           │
└─────────────────┘
        │
        │ fetch_fiction_page()
        ▼
┌─────────────────┐
│ Fiction Page    │ (HTML)
│ /fiction/123    │
└─────────────────┘
        │
        │ parse_fiction_page()
        ▼
┌─────────────────┐
│ Raw Data        │ (Dict)
│ {               │
│   title: str,   │
│   views: "1,234"│
│   rating: "4.5" │
│   ...           │
│ }               │
└─────────────────┘
        │
        │ normalize_fiction()
        ▼
┌─────────────────┐
│ Normalized Data │ (Dict)
│ {               │
│   title: str,   │
│   views: 1234,  │
│   rating: 4.5,  │
│   ...           │
│ }               │
└─────────────────┘
        │
        │ upsert_fictions()
        ▼
┌─────────────────┐
│ SQLite Database │
│ royalroad.db    │
│                 │
│ Table: fictions │
│ - fiction_id    │
│ - title         │
│ - author        │
│ - views         │
│ - rating        │
│ - ...           │
└─────────────────┘
"""

# =============================================================================
# FILE DEPENDENCIES
# =============================================================================

"""
run_scrape.py
    ├── imports config.py
    ├── imports db.py
    │   └── imports config.py
    ├── imports scraper.py
    │   └── imports config.py
    ├── imports parser.py
    │   └── imports config.py
    ├── imports normalizer.py
    └── imports loader.py
        └── imports db.py

test_pipeline.py
    └── imports all modules (same as run_scrape.py)

simple_scrapper.py
    └── standalone (original prototype)
"""

# =============================================================================
# USAGE EXAMPLES
# =============================================================================

if __name__ == "__main__":
    print(__doc__)
    
    print("\n" + "="*70)
    print("QUICK USAGE EXAMPLES")
    print("="*70)
    
    print("\n1. Test the pipeline:")
    print("   python test_pipeline.py")
    
    print("\n2. Run a small scrape (edit config.py first):")
    print("   python run_scrape.py")
    
    print("\n3. Query the database:")
    print("""
    from db import get_session, Fiction
    
    session = get_session()
    top_rated = session.query(Fiction)\\
        .order_by(Fiction.avg_rating.desc())\\
        .limit(10)\\
        .all()
    
    for fiction in top_rated:
        print(f"{fiction.title} - {fiction.avg_rating}⭐")
    """)
    
    print("\n4. Export to CSV:")
    print("""
    import pandas as pd
    from sqlalchemy import create_engine
    
    engine = create_engine('sqlite:///royalroad.db')
    df = pd.read_sql_table('fictions', engine)
    df.to_csv('royalroad_data.csv', index=False)
    """)
