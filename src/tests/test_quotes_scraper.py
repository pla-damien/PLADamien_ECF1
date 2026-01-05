# src/tests/test_quotes_scraper.py
from src.scrapers.quotes_scraper import QuotesScraper
from src.storage.MongoDB_quotes import MongoQuotesManager
import logging

def test_scrape_quotes():
    scraper = QuotesScraper()

    # Scrape les 2 premières pages pour le test
    quotes = scraper.scrape_quotes(max_pages=2)
    return quotes
    print(f"✅ {len(quotes)} citations scrapées")


if __name__ == "__main__":
    manager = MongoQuotesManager(uri="mongodb://admin:admin123@localhost:27017")
    scraper = QuotesScraper()
    inserted = manager.upsert_quotes(test_scrape_quotes())
    print(f"📚 {inserted} nouveau(x) livre(s) inséré(s).")  # Affiche "1"
    manager.close()
