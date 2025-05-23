-- Création de la table attached_schools
CREATE TABLE IF NOT EXISTS attached_schools (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    school_id INTEGER NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, school_id)
);

-- Création d'un index pour améliorer les performances des requêtes
CREATE INDEX IF NOT EXISTS idx_attached_schools_user_id ON attached_schools(user_id);
CREATE INDEX IF NOT EXISTS idx_attached_schools_school_id ON attached_schools(school_id);

-- Création d'un trigger pour mettre à jour le champ updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_attached_schools_updated_at
    BEFORE UPDATE ON attached_schools
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column(); 