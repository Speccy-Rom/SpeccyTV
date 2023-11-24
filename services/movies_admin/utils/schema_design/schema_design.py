import os

import psycopg2

if __name__ == "__main__":
    dsl = {
        'dbname': os.environ.get('POSTGRES_NAME', 'movies'),
        'user': os.environ.get('POSTGRES_USER', 'postgres'),
        'host': os.environ.get('POSTGRES_HOST', 'localhost'),
        'port': os.environ.get('POSTGRES_PORT', '5432'),
        'password': os.environ.get('POSTGRES_PASSWORD', 'postgres'),
    }

    SQL = """
    CREATE SCHEMA IF NOT EXISTS content;
    CREATE TABLE IF NOT EXISTS content.genre (
        id UUID PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        created TIMESTAMP WITH TIME ZONE,
        modified TIMESTAMP WITH TIME ZONE
    );
    CREATE TABLE IF NOT EXISTS content.film_work (
        id UUID PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT,
        creation_date DATE,
        certificate TEXT,
        file_path TEXT NOT NULL,
        rating FLOAT,
        type TEXT NOT NULL,
        created TIMESTAMP WITH TIME ZONE,
        modified TIMESTAMP WITH TIME ZONE
    );
    CREATE TABLE IF NOT EXISTS content.person (
        id UUID PRIMARY KEY,
        full_name TEXT NOT NULL,
        birth_date DATE,
        created TIMESTAMP WITH TIME ZONE,
        modified TIMESTAMP WITH TIME ZONE
    );
    CREATE TABLE IF NOT EXISTS content.person_film_work (
        id UUID PRIMARY KEY,
        film_work_id UUID NOT NULL,
        person_id UUID NOT NULL,
        role TEXT NOT NULL,
        created TIMESTAMP WITH TIME ZONE
    );
    CREATE TABLE IF NOT EXISTS content.genre_film_work (
        id UUID PRIMARY KEY,
        film_work_id UUID NOT NULL,
        genre_id UUID NOT NULL,
        created TIMESTAMP WITH TIME ZONE
    );
    CREATE TABLE IF NOT EXISTS content.file (
        id UUID PRIMARY KEY,
        file_path TEXT NOT NULL,
        file_format TEXT NOT NULL,
        video_codec TEXT NOT NULL,
        video_width INTEGER NOT NULL,
        video_height INTEGER NOT NULL,
        video_fps INTEGER NOT NULL,
        audio_codec TEXT NOT NULL,
        audio_sample_rate INTEGER NOT NULL,
        audio_channels INTEGER NOT NULL,
        created TIMESTAMP WITH TIME ZONE,
        modified TIMESTAMP WITH TIME ZONE
    );
    CREATE TABLE IF NOT EXISTS content.file_film_work (
        id UUID PRIMARY KEY,
        film_work_id UUID NOT NULL,
        file_id UUID NOT NULL,
        created TIMESTAMP WITH TIME ZONE
    );
    CREATE UNIQUE INDEX film_work_genre ON content.genre_film_work (film_work_id, genre_id);
    CREATE UNIQUE INDEX film_work_person_role ON content.person_film_work (film_work_id, person_id, role);
    CREATE UNIQUE INDEX film_work_file ON content.file_film_work (film_work_id, file_id);
    """

    with psycopg2.connect(**dsl) as conn, conn.cursor() as cursor:
        try:
            cursor.execute(SQL)
            print('Schema content is created.')
        except psycopg2.errors.DuplicateTable:
            print('Schema content already exists.')
    conn.close()
