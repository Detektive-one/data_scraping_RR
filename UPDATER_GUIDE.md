# Database Updater Guide

This guide explains how to update your existing scraped database with new fields (`fiction_type`, `warning_tags`, `content_warnings`, etc.) without re-scraping the entire dataset.

## 🚀 How to Run the Update

1. **Migrate the Database** (One-time setup)
   This adds the new empty columns to your existing `royalroad.db`.
   ```bash
   python migrate_db.py
   ```
   *Output should show "Added column..." or "Column already exists".*

2. **Run the Updater**
   This script iterates through all fictions in your database, fetches them again, and updates the missing fields.
   ```bash
   python update_db.py
   ```

## ⏸ Pause and Resume

The updater has a built-in **checkpoint system** (`update_checkpoint.json`).

- **To Pause**: Press `Ctrl+C`. The script will finish the current fiction, save progress, and exit.
- **To Resume**: Just run `python update_db.py` again. It will automatically detect the checkpoint and continue from where it left off.

## 📊 What Gets Updated

For every fiction in your database, it will populate:
- **Fiction Type**: "Original" or "Fanfiction"
- **Status**: "Ongoing", "Completed", "Hiatus", etc.
- **Last Updated**: Exact timestamp (e.g., `2023-10-25T15:59:55`)
- **Warning Tags**: "Gore", "Profanity", "Sexual Content", etc. (from tags)
- **Content Warnings**: "AI-Assisted Content", "Mature Content", etc. (from labels and warning box)

## ⏱ Time Estimation

With 55,000+ novels, the update process will take time because we must respect rate limits to avoid bans.

- **Rate**: ~0.6-0.8 seconds per novel
- **Estimate**: ~10-12 hours for 55k novels

**Tip**: You can run this in the background or over several sessions using the pause/resume feature.
