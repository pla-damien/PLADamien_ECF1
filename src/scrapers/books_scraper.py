import requests
from bs4 import BeautifulSoup
from .config import BASE_URL, USER_AGENT

class BooksScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})

    def scrape_book_page(self, url):
        response = self.session.get(url)
        if response.status_code != 200:
            raise Exception(f"Échec de la récupération de {url}")

        soup = BeautifulSoup(response.text, "html.parser")
        books = []

        for book in soup.select("article.product_pod"):
            title = book.h3.a["title"]

            # Gestion robuste du prix
            price_text = book.select_one("p.price_color").text
            price = float(price_text.replace("£", "").replace("Â", "").strip())

            rating = book.p["class"][1]  # "One", "Two", ..., "Five"
            url = book.h3.a["href"]
            full_url = f"{BASE_URL}/catalogue/{url}" if "catalogue" not in url else f"{BASE_URL}/{url}"

            books.append({
                "title": title,
                "price": price,
                "rating": rating,
                "url": full_url,
            })

        next_page = soup.select_one("li.next a")
        next_page_url = next_page["href"] if next_page else None
        return books, next_page_url

    def scrape_all_books(self, start_url=None):
        """Scrape tous les livres en paginant."""
        if start_url is None:
            start_url = f"{BASE_URL}/catalogue/page-1.html"

        all_books = []
        current_url = start_url

        while current_url:
            books, current_url = self.scrape_book_page(current_url)
            all_books.extend(books)
            if current_url:
                current_url = f"{BASE_URL}/catalogue/{current_url}"

        return all_books