CREATE TABLE librairies (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    adresse TEXT NOT NULL,
    code_postal VARCHAR(10),
    ville VARCHAR(50),
    telephone VARCHAR(20) CHECK (telephone ~ '^[0-9+() -]+$'),
    email VARCHAR(100) CHECK (email ~* '^[A-Za-z0-9._%-]+@[A-Za-z0-9.-]+[.][A-Za-z]+$'),
    site_web VARCHAR(255),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_mise_a_jour TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    est_partenaire BOOLEAN DEFAULT TRUE,
    notes TEXT
);