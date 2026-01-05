# src/scrapers/quotes_scraper.py
from bs4 import BeautifulSoup
import requests
from typing import List, Dict, Optional, Tuple
import logging
from urllib.parse import urljoin

# Configuration
BASE_URL = "https://quotes.toscrape.com"
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

class QuotesScraper:
    """Scraper pour extraire les citations depuis quotes.toscrape.com"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })

    def scrape_quotes(self, max_pages: Optional[int] = None) -> List[Dict]:
        """Scrape toutes les citations (avec limite optionnelle de pages)"""
        quotes = []
        current_url = BASE_URL
        page_count = 0

        while current_url:
            if max_pages and page_count >= max_pages:
                break

            logging.info(f"Scraping page {page_count + 1}: {current_url}")
            page_quotes, next_page_url = self._scrape_page(current_url)
            quotes.extend(page_quotes)
            current_url = urljoin(BASE_URL, next_page_url) if next_page_url else None
            page_count += 1

        return quotes

    def _scrape_page(self, url: str) -> Tuple[List[Dict], Optional[str]]:
        """Scrape une seule page et retourne les citations + URL de la page suivante"""
        try:
            response = self.session.get(url)
            response.raise_for_status()
            response.encoding = 'utf-8'  # Force l'encodage

            soup = BeautifulSoup(response.text, 'html.parser')
            quotes = []

            for quote in soup.select("div.quote"):
                quotes.append({
                    "text": quote.select_one("span.text").get_text(strip=True).replace('“', '').replace('”', ''),
                    "author": quote.select_one("small.author").get_text(strip=True),
                    "author_url": urljoin(BASE_URL, quote.select_one("a")["href"]),
                    "tags": [tag.get_text(strip=True) for tag in quote.select("div.tags a.tag")]
                })

            next_page = soup.select_one("li.next a")
            return quotes, next_page["href"] if next_page else None

        except Exception as e:
            logging.error(f"Erreur lors du scraping de {url}: {str(e)}")
            return [], None


