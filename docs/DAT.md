# 📘 Dossier d’Architecture Technique (DAT)
**Projet : ECF1 – Pipeline de données (Scraping → MongoDB → PostgreSQL)**  
**Auteur : Damien PLA**

---

## 1. Choix d’architecture globale

### 1.1 Architecture retenue
L’architecture mise en place repose sur un **Data Lake simplifié**, composé de deux briques principales :

- **MongoDB** pour le stockage des données brutes issues du scraping (zone *Raw / Bronze*)
- **PostgreSQL** pour le stockage des données transformées et exploitables (zone *Curated / Gold*)

Cette architecture suit une logique **ETL (Extract – Transform – Load)**.

---

### 1.2 Justification du choix
Les données collectées par scraping sont :
- semi-structurées
- hétérogènes
- susceptibles d’évoluer dans le temps

MongoDB permet de stocker ces données sans contrainte de schéma strict, tandis que PostgreSQL permet de structurer et d’exploiter les données via SQL.

---

### 1.3 Alternatives et comparaison
- **Data Warehouse uniquement**  
  ❌ Peu adapté au stockage de données brutes issues du scraping
- **Lakehouse (Delta Lake, Iceberg)**  
  ❌ Architecture trop complexe pour le périmètre du projet
- **NoSQL uniquement**  
  ❌ Capacités analytiques limitées

---

### 1.4 Avantages et inconvénients

**Avantages**
- Séparation claire des responsabilités
- Scalabilité sur les données brutes
- Exploitation SQL performante
- Architecture professionnelle et pédagogique

**Inconvénients**
- Duplication des données entre MongoDB et PostgreSQL
- Maintenance du pipeline ETL
- Pas de moteur analytique distribué

---

## 2. Choix des technologies

### 2.1 Stockage des données brutes
**MongoDB**
- Stockage de documents JSON
- Schéma flexible
- Gestion des doublons via index unique

**Alternative**
- Fichiers JSON/CSV  
  ❌ Pas de requêtage avancé  
  ❌ Pas de contrôle d’unicité

---

### 2.2 Données transformées
**PostgreSQL**
- Modèle relationnel
- Intégrité référentielle
- Support SQL standard

**Alternative**
- MySQL  
  ❌ Moins riche fonctionnellement
- SQLite  
  ❌ Peu adapté à un usage serveur

---

### 2.3 Interrogation SQL
**PostgreSQL**
- SQL avancé
- Index, contraintes, jointures
- Outil standard du monde data

**Alternative**
- DuckDB  
  ❌ Moins orienté production
- BigQuery / Snowflake  
  ❌ Hors périmètre ECF

---

## 3. Organisation des données

### 3.1 Architecture des couches
L’architecture est organisée en couches :

| Couche | Rôle | Technologie |
|------|----|-----------|
| Raw / Bronze | Données brutes scrapées | MongoDB |
| Transform / Silver | Nettoyage et enrichissement | Python |
| Curated / Gold | Données finales exploitables | PostgreSQL |

---

### 3.2 Couches de transformation
- Conversion des prix GBP → EUR
- Normalisation des notes
- Gestion du stock
- Création des relations métier

---

### 3.3 Convention de nommage
- Tables : `snake_case`
- Colonnes :
  - dates : `created_at`, `updated_at`, `scraped_at`
  - clés étrangères : `<entite>_id`
- Collections MongoDB : `books`
- Bases :
  - `ecf_data_lake`
  - `ECF_db`

---

## 4. Modélisation des données

### 4.1 Modèle retenu
Modèle relationnel normalisé (3NF).

---

### 4.2 Schéma des données

**Table `category`**
- id (PK)
- name (unique)
- created_at

**Table `books`**
- id (PK)
- title
- price
- category_id (FK)
- description
- rating
- stock
- scraped_at
- created_at
- updated_at

---

### 4.3 Diagramme entité–relation

