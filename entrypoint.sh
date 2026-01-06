#!/bin/sh
set -e

echo "📚 Lancement du scraper books_scraper.py..."
python -m src.scrapers.books_scraper

echo "✅ Scraping terminé avec succès"

echo "🚀 Lancement du pipeline..."
python pipeline.py

echo "✅ Pipeline terminé avec succès"
