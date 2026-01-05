CREATE TABLE librairies (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    adresse TEXT NOT NULL,
    code_postal VARCHAR(10),
    ville VARCHAR(50),
    contact_nom VARCHAR(50),
    email VARCHAR(100) CHECK (email ~* '^[A-Za-z0-9._%-]+@[A-Za-z0-9.-]+[.][A-Za-z]+$'),
    telephone VARCHAR(20) CHECK (telephone ~ '^[0-9+() -]+$'),
    ca_annuelle INT,
    date_partenariat DATE,
    specialite VARCHAR(50),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8)
);