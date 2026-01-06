# src/repositories/mongo_quote.py
from pymongo import MongoClient, UpdateOne
from pymongo.errors import PyMongoError, BulkWriteError
from typing import List, Dict
import logging
from datetime import datetime

class MongoQuotesManager:
    """
    Gère l'insertion des citations (quotes) dans MongoDB avec un comportement "upsert".
    - Insère uniquement les nouvelles citations (basé sur un champ unique comme `text` ou un hash).
    - Ne met pas à jour les citations existantes.
    - Ajoute des métadonnées automatiques (date d'insertion, source).
    """

    def __init__(
        self,
        uri: str = "mongodb://localhost:27017",
        db_name: str = "ecf_data_lake",
        collection_name: str = "quotes"  # Nom de la collection pour les quotes
    ):
        """
        Initialise la connexion à MongoDB et configure les index.

        Args:
            uri (str): URI de connexion MongoDB (ex: "mongodb://user:pass@host:port").
            db_name (str): Nom de la base de données.
            collection_name (str): Nom de la collection (par défaut: "quotes_clean").
        """
        self.uri = uri
        self.db_name = db_name
        self.collection_name = collection_name
        self.client = None
        self.db = None
        self.collection = None
        self._connect()

    def _connect(self) -> None:
        """Établit la connexion à MongoDB et crée un index unique."""
        try:
            self.client = MongoClient(self.uri)
            self.db = self.client[self.db_name]
            self.collection = self.db[self.collection_name]

            # Créer un index unique sur le champ `text` (ou un hash du texte pour éviter les conflits)
            # Note: Si deux citations ont le même texte mais des auteurs différents, utilisez un hash combiné.
            self.collection.create_index([("text", 1)], unique=True)
            logging.info(f"✅ Connecté à MongoDB: {self.uri}/{self.db_name} (collection: {self.collection_name})")

        except PyMongoError as e:
            logging.error(f"❌ Échec de la connexion à MongoDB: {e}")
            raise ConnectionError(f"Impossible de se connecter à MongoDB: {e}")

    def upsert_quotes(self, quotes: List[Dict]) -> int:
        """
        Insère les citations **uniquement si elles n'existent pas déjà** (basé sur le champ `text`).
        Utilise `update_many` avec `upsert=True` et `$setOnInsert` pour éviter les mises à jour.

        Args:
            quotes (List[Dict]): Liste de dictionnaires représentant les citations.
                                Chaque citation doit avoir un champ `text` (unique).

        Returns:
            int: Nombre de citations **nouvellement insérées** (0 si toutes existaient déjà).
        """
        if not quotes:
            logging.warning("⚠️ Aucune citation à insérer.")
            return 0

        try:
            operations = []
            for quote in quotes:
                # Utiliser $setOnInsert pour ne définir les champs QU'à l'insertion
                operation = UpdateOne(
                    {"text": quote["text"]},  # Critère de recherche (champ unique)
                    {
                        "$setOnInsert": {
                            **quote,
                            "metadata": {
                                "inserted_at": datetime.utcnow(),
                                "source": "scraping"
                            }
                        }
                    },
                    upsert=True  # Insère si le document n'existe pas
                )
                operations.append(operation)

            # Exécuter en bulk pour les performances
            result = self.collection.bulk_write(operations, ordered=False)
            inserted_count = result.upserted_count
            logging.info(f"💬 {inserted_count} nouvelles citations insérées. {len(quotes) - inserted_count} déjà existantes.")
            return inserted_count

        except BulkWriteError as e:
            logging.error(f"❌ Erreur lors de l'insertion des citations: {e.details}")
            return 0
        except PyMongoError as e:
            logging.error(f"❌ Erreur MongoDB: {e}")
            return 0

    def close(self) -> None:
        """Ferme la connexion à MongoDB."""
        if self.client:
            self.client.close()
            logging.info("🔌 Connexion MongoDB fermée.")
