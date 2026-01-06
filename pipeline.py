from src.scrapers.books_scraper import BooksScraper
from src.storage.MongoDB_books import MongoBooksManager
from dataclasses import dataclass
import requests
import psycopg2
from datetime import datetime

@dataclass
class book:
    title: str
    price: float
    description: str
    rating: str
    stock: str
    dispo: bool
    category: str
    created_at: datetime
    scraped_at: datetime

# ==========================TOOLS===============================
def get_change():
    try:
        # Utilisation de l'API gratuite de ExchangeRate-API
        response = requests.get("https://api.exchangerate-api.com/v4/latest/GBP")
        data = response.json()
        return data['rates']['EUR']
    except Exception as e:
        print(f"Erreur lors de la récupération du taux de change: {e}")
        return 1.16  # Valeur par défaut

def get_category(category: str):
    DNS = "dbname=ECF_db user=admin password=admin123 host=postgres port=5432"
    try:
        with psycopg2.connect(DNS) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id FROM category WHERE name = %s", (category,))
                response = cur.fetchone()
                if response:
                    return response[0]

    except psycopg2.OperationalError as e:
        print("Problème de connexion à la base de données:", e)
    except Exception as e:
        print("Erreur inattendue:", e)

# ==========================IMPORT===============================
def get_books():
    Mongo = MongoBooksManager(uri="mongodb://admin:admin123@mongodb:27017")
    books = Mongo.get_all_books()
    return books

def split_books(row):
    livre = book(
        title=row["title"],
        price=row["price"],  
        description=row["description"],
        rating=row["rating"],
        stock=row["stock"],
        dispo=False,  # Initialisation avec une valeur par défaut
        category=row["category"],
        created_at=datetime.utcnow(),
        scraped_at=row["metadata"]["inserted_at"]
    )
    return livre

# ==========================TRANSFORM===============================
def price_euro(price_livre):
    change = get_change()
    print("Change : ", change)
    price = round(change * price_livre, 2)  # Arrondir à 2 décimales
    return price

def rating_int(rate: str):
    match rate:
        case "One":
            return 1
        case "Two":
            return 2
        case "Three":
            return 3
        case "Four":
            return 4
        case "Five":
            return 5
        case _:
            return 0

def stock_book(stock):
    return stock == "In stock"

# ==========================EXPORT===============================
def storage_category(name: str):
    DNS = "dbname=ECF_db user=admin password=admin123 host=postgres port=5432"
    with psycopg2.connect(DNS) as conn:
        with conn.cursor() as cur:
            try:
                cur.execute("INSERT INTO category (name, created_at) VALUES (%s, %s);", (name, datetime.utcnow()))
                conn.commit()  # Ajout de conn.commit() pour valider la transaction
            except psycopg2.errors.SyntaxError as e:
                print(f"Erreur SQL pour {name}: ", e)
            except psycopg2.errors.UniqueViolation as e:
                print(f"Violation Unique pour {name}: ", e)
            except psycopg2.OperationalError as e:
                print(f"Problème de connection pour {name}: ", e)
            except Exception as e:
                print(f"Autre erreur pour {name}: ", e)

def storage_book(book: book):
    DNS = "dbname=ECF_db user=admin password=admin123 host=postgres port=5432"
    try:
        with psycopg2.connect(DNS) as conn:
            with conn.cursor() as cur:
                try:
                    # Convertir la note en entier
                    rating_int_value = rating_int(book.rating)

                    # Convertir le stock en booléen
                    stock_bool = stock_book(book.stock)

                    cur.execute("""
                        INSERT INTO books
                        (title, price, category_id, description, rating, stock, scraped_at, created_at, updated_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        book.title,
                        book.price,
                        book.category,
                        book.description,
                        rating_int_value,
                        stock_bool,
                        book.scraped_at,
                        book.created_at,
                        book.created_at
                    ))
                    conn.commit()  # Ajout de conn.commit() pour valider la transaction
                    print(f"✅ Livre {book.title} inséré avec succès")
                except psycopg2.errors.SyntaxError as e:
                    print(f"Erreur SQL pour {book.title}: ", e)
                except psycopg2.errors.UniqueViolation as e:
                    print(f"Violation Unique pour {book.title}: ", e)
                except psycopg2.OperationalError as e:
                    print(f"Problème de connection pour {book.title}: ", e)
                except Exception as e:
                    print(f"Autre erreur pour {book.title}: ", e)

    except psycopg2.OperationalError as e:
        print("Problème de connexion à la base de données:", e)
    except Exception as e:
        print("Erreur inattendue:", e)

def main():

    scraper = BooksScraper()
    books = scraper.scrape_all_books()
    manager = MongoBooksManager(uri="mongodb://admin:admin123@mongodb:27017")
    inserted = manager.upsert_books(books)
    print(f"📚 {inserted} nouveau(x) livre(s) inséré(s).")  # Affiche "1"
    manager.close()


    all_books = get_books()
    for row in all_books:
        one_book = split_books(row)
        print("book price " ,one_book.price )
        one_book.price = price_euro(one_book.price)
        
        one_book.dispo = stock_book(one_book.stock)

        # Récupérer l'ID de la catégorie
        category_id = get_category(one_book.category)
        if category_id is None:
            storage_category(one_book.category)
            category_id = get_category(one_book.category)

        one_book.category = category_id
        one_book.created_at = datetime.utcnow()

        storage_book(one_book)

if __name__ == "__main__":
    main()
