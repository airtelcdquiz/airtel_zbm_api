-- Migration pour ajouter les colonnes de suivi du traitement des documents
-- Date: 2024-03-19

-- Ajout des nouvelles colonnes
ALTER TABLE documents
    ADD COLUMN current_page INT DEFAULT 0,
    ADD COLUMN total_pages INT,
    ADD COLUMN retry_count INT DEFAULT 0,
    ADD COLUMN last_retry_at DATETIME,
    ADD COLUMN processing_result JSON,
    ADD COLUMN processing_status VARCHAR(20) NOT NULL DEFAULT 'pending',
    ADD COLUMN processing_error TEXT,
    ADD COLUMN processed_at DATETIME;

-- Création d'un index sur processing_status pour optimiser les requêtes de statut
CREATE INDEX idx_documents_processing_status ON documents(processing_status);

-- Création d'un index sur last_retry_at pour optimiser les requêtes de reprise
CREATE INDEX idx_documents_last_retry_at ON documents(last_retry_at);

-- Commentaires sur les colonnes pour la documentation
ALTER TABLE documents
    MODIFY COLUMN current_page INT DEFAULT 0 COMMENT 'Page en cours de traitement du document',
    MODIFY COLUMN total_pages INT COMMENT 'Nombre total de pages dans le document',
    MODIFY COLUMN retry_count INT DEFAULT 0 COMMENT 'Nombre de tentatives de traitement',
    MODIFY COLUMN last_retry_at DATETIME COMMENT 'Date et heure de la dernière tentative',
    MODIFY COLUMN processing_result JSON COMMENT 'Résultats détaillés du traitement au format JSON',
    MODIFY COLUMN processing_status VARCHAR(20) NOT NULL DEFAULT 'pending' COMMENT 'Statut du traitement: pending, processing, completed, failed',
    MODIFY COLUMN processing_error TEXT COMMENT 'Message d''erreur en cas d''échec du traitement',
    MODIFY COLUMN processed_at DATETIME COMMENT 'Date et heure de fin du traitement';

-- Script de rollback (en cas de besoin)
/*
ALTER TABLE documents
    DROP COLUMN current_page,
    DROP COLUMN total_pages,
    DROP COLUMN retry_count,
    DROP COLUMN last_retry_at,
    DROP COLUMN processing_result,
    DROP COLUMN processing_status,
    DROP COLUMN processing_error,
    DROP COLUMN processed_at;

DROP INDEX idx_documents_processing_status ON documents;
DROP INDEX idx_documents_last_retry_at ON documents;
*/ 