from src.scrapers.books_scraper import BooksScraper
from src.storage.MongoDB_books import MongoDBManager



def test_scrape_books():
    scraper = BooksScraper()
    books = scraper.scrape_all_books()
    return books

if __name__ == "__main__":
    manager = MongoDBManager(uri="mongodb://admin:admin123@localhost:27017")
    inserted = manager.upsert_books(test_scrape_books())
    print(f"📚 {inserted} nouveau(x) livre(s) inséré(s).")  # Affiche "1"
    manager.close()