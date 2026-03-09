CREATE TABLE documents (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description VARCHAR(500),
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER,
    mime_type VARCHAR(100) DEFAULT 'application/pdf',
    uploaded_by VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_documents_user
        FOREIGN KEY (uploaded_by)
        REFERENCES users(phone_number)
);

-- Création d'un index sur uploaded_by pour améliorer les performances des requêtes
CREATE INDEX idx_documents_uploaded_by ON documents(uploaded_by);

-- Création d'un index sur created_at pour les requêtes de tri par date
CREATE INDEX idx_documents_created_at ON documents(created_at);