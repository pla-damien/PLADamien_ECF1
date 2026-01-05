import pandas as pd 
import logging
import psycopg2
import requests
 #Chemin dufichier a intégrer dans postgres
path = "./data/partenaire_librairies.xlsx"

DNS = "dbname=ECF_db user=admin password=admin123 host=localhost port=5432"




def verif_adress(adress,city):
    adress_format = f"{adress} {city}"
    param = {"q": adress_format, "limit": 1}

    try:
        response = requests.get("https://api-adresse.data.gouv.fr/search/", params=param)
        print("Status Code:", response.status_code)

        # Vérifie si la requête a réussi (status_code 200)
        if response.status_code != 200:
            print(f"Erreur HTTP {response.status_code} pour {adress_format}")
            return None, None

        result = response.json()

        # Vérifie si des résultats existent
        if not result.get("features"):
            print(f"Aucune adresse trouvée pour {adress_format}")
            return None, None

        # Accès sécurisé aux données
        try:
            longitude = result["features"][0]["geometry"]["coordinates"][0]
            latitude = result["features"][0]["geometry"]["coordinates"][1]
            print("Coordonnées:", longitude, latitude)
            return longitude, latitude
        except (KeyError, IndexError) as e:
            print(f"Format de réponse inattendu pour {adress_format}: {e}")
            return None, None

    except requests.exceptions.RequestException as e:
        print(f"Erreur de requête pour {adress_format}: {e}")
        return None, None
try:
    df = pd.read_excel(path, engine="openpyxl")
    logging.info("✅ Fichier XLSX lu avec succès.")

    # Afficher les colonnes disponibles
    print("Colonnes disponibles dans le DataFrame:")
    print(df.columns.tolist())

except Exception as e:
    logging.error(f"❌ Erreur lors de la lecture du fichier XLSX: {e}")
    raise

# Vérifiez que toutes les colonnes nécessaires existent
required_columns = [
    'nom_librairie', 'adresse', 'code_postal', 'ville',
    'contact_nom', 'contact_email', 'contact_telephone',
    'ca_annuel', 'date_partenariat', 'specialite'
]

missing_columns = [col for col in required_columns if col not in df.columns]
if missing_columns:
    raise ValueError(f"Les colonnes suivantes sont manquantes dans le fichier Excel: {missing_columns}")

# Connexion à PostgreSQL
try:
    with psycopg2.connect(DNS) as conn:
        with conn.cursor() as cur:
            for index, row in df.iterrows():
                print(f"Traitement de la librairie: {row['contact_nom']}")

                # Récupération des coordonnées
                longitude, latitude = verif_adress(row["adresse"], row["ville"])

                # Préparation des valeurs pour l'INSERT
                values = (
                    row["contact_nom"],
                    row["adresse"],
                    row["code_postal"],
                    row["ville"],
                    row["contact_nom"],
                    row["contact_email"],
                    row["contact_telephone"],
                    row["ca_annuel"],
                    row["date_partenariat"],
                    row["specialite"],
                    latitude,
                    longitude
                )

                # Requête SQL corrigée
                query = """
                    INSERT INTO librairies (
                        nom, adresse, code_postal, ville, contact_nom, email,
                        telephone, ca_annuelle, date_partenariat, specialite,
                        latitude, longitude
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """

                try:
                    cur.execute(query, values)
                    conn.commit()
                    print(f"✅ Librairie {row['contact_nom']} insérée avec succès")
                except psycopg2.errors.SyntaxError as e:
                    print(f"Erreur SQL pour {row['contact_nom']}: ", e)
                except psycopg2.errors.UniqueViolation as e:
                    print(f"Violation Unique pour {row['contact_nom']}: ", e)
                except psycopg2.OperationalError as e:
                    print(f"Problème de connection pour {row['contact_nom']}: ", e)
                except Exception as e:
                    print(f"Autre erreur pour {row['contact_nom']}: ", e)

except psycopg2.OperationalError as e:
    print("Problème de connexion à la base de données:", e)
except Exception as e:
    print("Erreur inattendue:", e)