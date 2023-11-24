import json
import sqlite3
from typing import List


class SQLiteLoader:
    """Loads data from SQLite.
    Loads data from SQLite, converts it and returns a list of dictionaries
    for The dictionary list can be processed by PostgresSaver.
    """

    SQL = """
    WITH x as (
        SELECT m.id, group_concat(a.id) AS actors_ids, group_concat(a.name) AS actors_names
        FROM movies m
        LEFT JOIN movie_actors ma ON m.id = ma.movie_id
        LEFT JOIN actors a ON ma.actor_id = a.id
        GROUP BY m.id
    )
    SELECT m.id, genre, director, title, plot, imdb_rating, x.actors_ids, x.actors_names,
    CASE
    WHEN m.writers = '' THEN '[{"id": "' || m.writer || '"}]' ELSE m.writers END AS writers
    FROM movies m
    LEFT JOIN x ON m.id = x.id
    """

    def __init__(self, connection: sqlite3.Connection):
        self.conn = connection
        self.conn.row_factory = self.dict_factory

    @staticmethod
    def dict_factory(cursor: sqlite3.Cursor, row: tuple) -> dict:
        """Factory for strings as dict."""
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def load_writers_names(self) -> dict:
        """Getting a dict of all the writers."""
        writers = {}
        SQL = """
        SELECT DISTINCT id, name FROM writers
        """
        for writer in self.conn.execute(SQL):
            writers[writer['id']] = writer
        return writers

    def _transform_row(self, row: dict, writers: dict) -> dict:
        """Converting data from SQLite."""
        movie_writers = []
        writers_set = set()
        for writer in json.loads(row['writers']):
            writer_id = writer['id']
            if writers[writer_id]['name'] != 'N/A' and writer_id not in writers_set:
                movie_writers.append(writers[writer_id])
                writers_set.add(writer_id)

        actors_names = []
        if row['actors_ids'] is not None and row['actors_names'] is not None:
            actors_names = [x for x in row['actors_names'].split(',') if x != 'N/A']

        return {
            'id': row['id'],
            'genre': row['genre'].replace(' ', '').split(','),
            'actors': actors_names,
            'writers': [x['name'] for x in movie_writers],
            'imdb_rating': float(row['imdb_rating'])
            if row['imdb_rating'] != 'N/A'
            else None,
            'title': row['title'],
            'director': [x.strip() for x in row['director'].split(',')]
            if row['director'] != 'N/A'
            else None,
            'description': row['plot'] if row['plot'] != 'N/A' else None,
        }

    def load_movies(self) -> List[dict]:
        """Basic method for unloading data from MySQL."""
        movies = []
        writers = self.load_writers_names()

        for row in self.conn.execute(self.SQL):
            transformed_row = self._transform_row(row, writers)
            movies.append(transformed_row)

        return movies
