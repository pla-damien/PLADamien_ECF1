# mongo_manager.py (version avec upsert)
from pymongo import MongoClient, UpdateOne
from pymongo.errors import PyMongoError, BulkWriteError
from typing import List, Dict, Optional
import logging
from datetime import datetime

class MongoBooksManager:
    def __init__(
        self,
        uri: str = "mongodb://localhost:27017",
        db_name: str = "ecf_data_lake",
        collection_name: str = "books"
    ):
        self.uri = uri
        self.db_name = db_name
        self.collection_name = collection_name
        self.client = None
        self.db = None
        self.collection = None
        self._connect()

    def _connect(self) -> None:
        try:
            self.client = MongoClient(self.uri)
            self.db = self.client[self.db_name]
            self.collection = self.db[self.collection_name]

            # Index unique sur 'url' pour garantir l'unicité
            self.collection.create_index([("url", 1)], unique=True)
            logging.info(f"✅ Connecté à MongoDB: {self.uri}/{self.db_name}")

        except PyMongoError as e:
            logging.error(f"❌ Échec de la connexion à MongoDB: {e}")
            raise ConnectionError(f"Impossible de se connecter à MongoDB: {e}")

    def upsert_books(self, books: List[Dict]) -> int:
        """
        Insère les livres **uniquement s'ils n'existent pas déjà** (basé sur le champ 'url').
        Utilise `update_many` avec `upsert=True` mais **sans modifier** les documents existants.

        Args:
            books (List[Dict]): Liste de dictionnaires représentant les livres.

        Returns:
            int: Nombre de livres **nouvellement insérés** (0 si tous existaient déjà).
        """
        if not books:
            logging.warning("⚠️ Aucune donnée à insérer.")
            return 0

        try:
            # Préparer les opérations d'upsert
            operations = []
            for book in books:
                # On utilise $setOnInsert pour ne définir les champs QU'à l'insertion (pas en update)
                operation = UpdateOne(
                    {"url": book["url"]},  # Critère de recherche (champ unique)
                    {
                        "$setOnInsert": {
                            **book,
                            "metadata": {
                                "inserted_at": datetime.utcnow(),
                                "source": "scraping"
                            }
                        }
                    },
                    upsert=True  # Insère si le document n'existe pas
                )
                operations.append(operation)

            # Exécuter en bulk
            result = self.collection.bulk_write(operations, ordered=False)

            # Nombre de livres insérés (upserted_count = nouveaux documents)
            inserted_count = result.upserted_count
            logging.info(f"💾 {inserted_count} nouveaux livres insérés. {len(books) - inserted_count} déjà existants.")
            return inserted_count

        except BulkWriteError as e:
            logging.error(f"Erreur lors de l'insertion: {e.details}")
            return 0

        except PyMongoError as e:
            logging.error(f"Erreur MongoDB: {e}")
            return 0

    def close(self) -> None:
        if self.client:
            self.client.close()
            logging.info("🔌 Connexion MongoDB fermée.")
