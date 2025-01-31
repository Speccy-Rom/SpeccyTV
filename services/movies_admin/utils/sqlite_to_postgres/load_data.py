import os
import sqlite3
import logging
from pathlib import Path

import psycopg2
from psycopg2.extensions import connection as _connection
from utils.loader import SQLiteLoader
from utils.saver import PostgresSaver

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_from_sqlite(connection: sqlite3.Connection, pg_conn: _connection):
    """Basic method for loading data from SQLite into Postgres."""
    try:
        postgres_saver = PostgresSaver(pg_conn)
        sqlite_loader = SQLiteLoader(connection)

        postgres_saver.save_all_data(sqlite_loader.load_movies())
        logger.info("Data loaded successfully from SQLite to Postgres.")
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        raise

if __name__ == '__main__':
    dsl = {
        'dbname': os.environ.get('POSTGRES_NAME', 'movies'),
        'user': os.environ.get('POSTGRES_USER', 'postgres'),
        'host': os.environ.get('POSTGRES_HOST', 'localhost'),
        'port': os.environ.get('POSTGRES_PORT', '5432'),
        'password': os.environ.get('POSTGRES_PASSWORD', 'postgres'),
    }
    sqlite_path = Path(__file__).parent.joinpath('db.sqlite')

    try:
        with sqlite3.connect(sqlite_path) as sqlite_conn, psycopg2.connect(
            **dsl
        ) as pg_conn:
            load_from_sqlite(sqlite_conn, pg_conn)
        sqlite_conn.close()
        pg_conn.close()
    except Exception as e:
        logger.error(f"Error connecting to databases: {e}")
        raise