-- Création de la table attached_schools
CREATE TABLE IF NOT EXISTS attached_schools (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    phone_number VARCHAR(255) NOT NULL REFERENCES users(phone_number) ON DELETE CASCADE,
    code VARCHAR(255) NOT NULL REFERENCES schools(code) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(phone_number, code)
);

-- Index pour améliorer les performances
CREATE INDEX IF NOT EXISTS idx_attached_schools_phone_number 
ON attached_schools(phone_number);

CREATE INDEX IF NOT EXISTS idx_attached_schools_code 
ON attached_schools(code);