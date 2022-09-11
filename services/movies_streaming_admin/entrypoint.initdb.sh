#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE SCHEMA IF NOT EXISTS content;
    CREATE TABLE IF NOT EXISTS content.film_work (
        id UUID PRIMARY KEY,
        title TEXT NOT NULL,
        certificate TEXT,
        file_path TEXT NOT NULL,
        created TIMESTAMP WITH TIME ZONE,
        modified TIMESTAMP WITH TIME ZONE
    );
    CREATE TABLE IF NOT EXISTS content.file (
        id UUID PRIMARY KEY,
        file_path TEXT NOT NULL,
        resolution TEXT NOT NULL,
        codec_name TEXT,
        display_aspect_ratio TEXT,
        fps INTEGER,
        created TIMESTAMP WITH TIME ZONE,
        modified TIMESTAMP WITH TIME ZONE
    );
    CREATE TABLE IF NOT EXISTS content.file_film_work (
        id UUID PRIMARY KEY,
        film_work_id UUID NOT NULL,
        file_id UUID NOT NULL,
        created TIMESTAMP WITH TIME ZONE
    );
    CREATE UNIQUE INDEX film_work_file ON content.file_film_work (film_work_id, file_id);
EOSQL