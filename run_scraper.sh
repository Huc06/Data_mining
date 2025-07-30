#!/bin/bash

echo "🚀 Starting TikTok Scraper..."
echo "📦 Activating virtual environment..."

# Navigate to the script directory
cd "$(dirname "$0")"

# Activate virtual environment
source venv/bin/activate

echo "✅ Virtual environment activated"
echo "🔍 Running TikTok scraper..."

# Run the Python script
python tiktok_scrape_with_comments.py

echo "🎉 Scraping completed!" 