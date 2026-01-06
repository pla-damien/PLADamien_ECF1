import requests
from bs4 import BeautifulSoup
from .config import BASE_URL, USER_AGENT
from typing import  Dict

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

            # Récupération du stock
            availability = book.select_one("p.instock.availability")
            stock = "In stock" if availability else "Out of stock"

            rating = book.p["class"][1]  # "One", "Two", ..., "Five"
            book_url = book.h3.a["href"]
            full_url = f"{BASE_URL}/catalogue/{book_url}" if "catalogue" not in book_url else f"{BASE_URL}/{book_url}"

            # Ajout de la récupération des détails du livre
            book_details = self.get_book_details(full_url)

            books.append({
                "title": title,
                "price": price,
                "rating": rating,
                "url": full_url,
                "stock": stock,
                "category": book_details.get("category", "Unknown Category"),
                "description": book_details.get("description", "No description available")
            })

        next_page = soup.select_one("li.next a")
        next_page_url = next_page["href"] if next_page else None

        # Vérification pour éviter la boucle infinie
        if next_page_url and "javascript:void(0)" in next_page_url:
            next_page_url = None

        return books, next_page_url

    def get_book_details(self, book_url: str) -> Dict:
        """Récupère les détails d'un livre à partir de son URL"""
        try:
            response = self.session.get(book_url)
            if response.status_code != 200:
                return {}

            soup = BeautifulSoup(response.text, "html.parser")


            # Récupération de la catégorie
            category_element = soup.select_one("ul.breadcrumb li:nth-of-type(3)")
            category = category_element.text.strip() if category_element else "Unknown Category"

            # Récupération de la description
            description_element = soup.select_one("#product_description + p")
            description = description_element.text.strip() if description_element else "No description available"

            return {
                "category": category,
                "description": description
            }

        except Exception as e:
            print(f"Erreur lors de la récupération des détails du livre {book_url}: {e}")
            return {
                "author": "Unknown Author",
                "category": "Unknown Category",
                "description": "No description available"
            }

    def scrape_all_books(self, start_url=None):
        """Scrape tous les livres en paginant."""
        if start_url is None:
            start_url = f"{BASE_URL}/catalogue/page-1.html"

        all_books = []
        current_url = start_url
        visited_urls = set()  # Ensemble pour suivre les URLs déjà visitées

        while current_url:
            print(f"Scraping page: {current_url}")  # Pour le débogage

            if current_url in visited_urls:
                print("URL déjà visitée, arrêt de la pagination")
                break

            visited_urls.add(current_url)

            books, current_url = self.scrape_book_page(current_url)
            all_books.extend(books)

            if current_url:
                current_url = f"{BASE_URL}/catalogue/{current_url}"

        return all_books
