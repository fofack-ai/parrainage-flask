-- Création de la base
CREATE DATABASE IF NOT EXISTS parrainage;
USE parrainage;

-- Table utilisateurs
CREATE TABLE utilisateurs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    matricule VARCHAR(50) UNIQUE NOT NULL,
    mot_de_passe VARCHAR(255) NOT NULL,
    telephone VARCHAR(20),
    photo VARCHAR(255) DEFAULT 'default.jpg',
    serie ENUM('TI-RSI', 'TI-PAM') NOT NULL,
    niveau ENUM('1', '2') NOT NULL,
    est_disponible BOOLEAN DEFAULT TRUE,
    date_inscription DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Table parrainages (1 parrain = 1 filleul exclusif)
CREATE TABLE parrainages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_filleul INT UNIQUE,
    id_parrain INT UNIQUE,
    date_parrainage DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_filleul) REFERENCES utilisateurs(id) ON DELETE CASCADE,
    FOREIGN KEY (id_parrain) REFERENCES utilisateurs(id) ON DELETE CASCADE
);

-- Insérer parrains existants (NIVEAU 2 UNIQUEMENT)
INSERT INTO utilisateurs (nom, matricule, mot_de_passe, telephone, serie, niveau, est_disponible) VALUES
-- TI-RSI
('Jean Koffi', 'TI-RSI2001', '$2b$12$hash', '+2250700000001', 'TI-RSI', '2', TRUE),
('Marie Traoré', 'TI-RSI2002', '$2b$12$hash', '+2250700000002', 'TI-RSI', '2', TRUE),
('Pierre Kouadio', 'TI-RSI2003', '$2b$12$hash', '+2250700000003', 'TI-RSI', '2', TRUE),
-- TI-PAM
('Alice Koné', 'TI-PAM2001', '$2b$12$hash', '+2250700000004', 'TI-PAM', '2', TRUE),
('Paul NGuessan', 'TI-PAM2002', '$2b$12$hash', '+2250700000005', 'TI-PAM', '2', TRUE),
('Sophie Bamba', 'TI-PAM2003', '$2b$12$hash', '+2250700000006', 'TI-PAM', '2', TRUE);