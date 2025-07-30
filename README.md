# TikTok Scraper with Comments

This project scrapes TikTok videos, captions, and comments for a specific hashtag.

## Setup Complete! ✅

The environment has been set up with:
- Python virtual environment (`venv/`)
- Required packages: `playwright`, `yt-dlp`, `pandas`
- Playwright browsers installed

## How to Run

### Option 1: Using the run script (Recommended)
```bash
./run_scraper.sh
```

### Option 2: Manual activation
```bash
# Activate virtual environment
source venv/bin/activate

# Run the scraper
python tiktok_scrape_with_comments.py

# Deactivate when done
deactivate
```

## Configuration

Edit the variables in `tiktok_scrape_with_comments.py`:
- `HASHTAG = "tiktokshop"` - Change this to your target hashtag
- `LIMIT = 5` - Number of videos to scrape
- `OUTPUT_DIR = "tiktok_data"` - Output directory

## Output Structure

The scraper creates:
```
tiktok_data/
├── videos/          # Downloaded MP4 files
├── captions/        # Video captions (.txt)
├── comments/        # Comments for each video (.txt)
└── metadata.csv     # Summary of all scraped data
```

## Troubleshooting

If you get "command not found" errors:
1. Make sure you're in the `ScrapeGraph_Data` directory
2. Always activate the virtual environment first: `source venv/bin/activate`
3. Use `python` (not `python3`) after activating the virtual environment 