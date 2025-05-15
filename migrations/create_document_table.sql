-- Création de la table documents
CREATE TABLE documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description VARCHAR(500),
    file_path VARCHAR(500) NOT NULL,
    file_size INT,
    mime_type VARCHAR(100) DEFAULT 'application/pdf',
    uploaded_by INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (uploaded_by) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Création d'un index sur uploaded_by pour améliorer les performances des requêtes
CREATE INDEX idx_documents_uploaded_by ON documents(uploaded_by);

-- Création d'un index sur created_at pour les requêtes de tri par date
CREATE INDEX idx_documents_created_at ON documents(created_at);