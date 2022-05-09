import os
from datetime import datetime
from typing import Any, Dict, List, Set
from uuid import uuid4

from psycopg2.extensions import connection as _connection


class PostgresSaver():
    """Processed data from SQLite."""

    def __init__(self, connection: _connection):
        self.conn = connection
        self.person_set: Set[str] = set()
        self.genres_set: Set[str] = set()
        self.film_work: List[dict] = []
        self.genre: List[dict] = []
        self.genre_film_work: List[dict] = []
        self.person: List[dict] = []
        self.person_film_work: List[dict] = []

    def append_film_work(self, row: Dict[str, Any]) -> str:
        """Adds a row to the local film_work table."""
        film_id = str(uuid4())
        self.film_work.append({
            'id': str(film_id),
            'title': row['title'],
            'description': '' if row['description'] is None else row['description'],
            'creation_date': None,
            'certificate': '',
            'file_path': None,
            'rating': row['imdb_rating'],
            'type': 'movie',
            'created': datetime.now().astimezone(),
            'modified': datetime.now().astimezone()
        })
        return film_id

    def _add_person(self, id: str, name: str):
        """Adds a row to the local person table."""
        self.person.append({
            'id': id,
            'full_name': name,
            'birth_date': None,
            'created': datetime.now().astimezone(),
            'modified': datetime.now().astimezone()
        })

    def append_person(self, person_list: List[str]) -> List[str]:
        """Adds several rows to the local person table.
        Adds several rows to the local person table and returns the uuid of all added person.
        Does not add a row if the person already exists in the table.
        """
        if person_list is None:
            return []

        id_list = []
        person_id = ''
        for person in person_list:
            if person not in self.person_set:
                person_id = str(uuid4())
                self._add_person(person_id, person)
                self.person_set.add(person)
            else:
                for p in self.person:
                    if p['full_name'] == person:
                        person_id = p['id']
                        break
            id_list.append(person_id)

        return id_list

    def _add_genre(self, id_: str, name: str):
        """Adds a row to the local genre table."""
        row = {
            "id": id_,
            "name": name,
            "description": "",
            "created": datetime.now().astimezone(),
            "modified": datetime.now().astimezone()
        }
        self.genre.append(row)

    def append_genre(self, genre_list: List[str]) -> List[str]:
        """Adds several rows to the local genre table.
        Adds several rows to the local genre table and returns the uuid of all added genres.
        Does not add a row if the genre is already in the table.
        """
        if genre_list is None:
            return []

        id_list = []
        genre_id = ''
        for genre in genre_list:
            if genre not in self.genres_set:
                genre_id = str(uuid4())
                self._add_genre(genre_id, genre)
                self.genres_set.add(genre)
            else:
                for g in self.genre:
                    if g['name'] == genre:
                        genre_id = g['id']
                        break
            id_list.append(genre_id)

        return id_list

    def append_person_film_work(self, film_id: str, person_id_list: List[str], role: str):
        """Adds a rows to the local person_film_work table."""
        for person_id in person_id_list:
            id_ = str(uuid4())
            row = {
                "id": id_,
                "film_work_id": film_id,
                "person_id": person_id,
                "role": role,
                "created": datetime.now().astimezone()
            }
            self.person_film_work.append(row)

    def append_genre_film_work(self, film_id: str, genre_id_list: List[str]):
        """Adds a rows to the local genre_film_work table."""
        for genre_id in genre_id_list:
            row = {
                'id': str(uuid4()),
                'film_work_id': film_id,
                'genre_id': genre_id,
                'created': datetime.now().astimezone()
            }
            self.genre_film_work.append(row)

    def insert_film_work(self):
        """Inserts data from the local film_work table into PostgreSQL."""
        with self.conn.cursor() as cursor:
            args = [tuple(val for val in row.values()) for row in self.film_work]
            args_bytes = b','.join(cursor.mogrify('(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', x) for x in args)
            cursor.execute(b'INSERT INTO content.film_work VALUES ' + args_bytes)

    def insert_genre(self):
        """Inserts data from the local film_work table into PostgreSQL."""
        with self.conn.cursor() as cursor:
            args = [tuple(val for val in row.values()) for row in self.genre]
            args_bytes = b','.join(cursor.mogrify('(%s, %s, %s, %s, %s)', x) for x in args)
            cursor.execute(b'INSERT INTO content.genre VALUES ' + args_bytes)

    def insert_person(self):
        """Inserts data from the local person table into PostgreSQL."""
        with self.conn.cursor() as cursor:
            args = [tuple(val for val in row.values()) for row in self.person]
            args_bytes = b','.join(cursor.mogrify('(%s, %s, %s, %s, %s)', x) for x in args)
            cursor.execute(b'INSERT INTO content.person VALUES ' + args_bytes)

    def insert_genre_film_work(self):
        """Inserts data from the local genre_film_work table into PostgreSQL."""
        with self.conn.cursor() as cursor:
            args = [tuple(val for val in row.values()) for row in self.genre_film_work]
            args_bytes = b','.join(cursor.mogrify('(%s, %s, %s, %s)', x) for x in args)
            cursor.execute(b'INSERT INTO content.genre_film_work VALUES ' + args_bytes)

    def insert_person_film_work(self):
        """Inserts data from local table person_film_work into PostgreSQL."""
        with self.conn.cursor() as cursor:
            args = [tuple(val for val in row.values()) for row in self.person_film_work]
            args_bytes = b','.join(cursor.mogrify('(%s, %s, %s, %s, %s)', x) for x in args)
            cursor.execute(b'INSERT INTO content.person_film_work VALUES '
                           + args_bytes
                           + b' ON CONFLICT (film_work_id, person_id, role) DO NOTHING')

    def save_all_data(self, data: List[dict]):
        """Basic method that processes data from MySQL and loads it into PostgreSQL."""
        for row in data:
            film_id = self.append_film_work(row)

            actor_id_list = self.append_person(row['actors'])
            self.append_person_film_work(film_id, actor_id_list, 'actor')

            writer_id_list = self.append_person(row['writers'])
            self.append_person_film_work(film_id, writer_id_list, 'writer')

            director_id_list = self.append_person(row['director'])
            self.append_person_film_work(film_id, director_id_list, 'director')

            genre_id_list = self.append_genre(row['genre'])
            self.append_genre_film_work(film_id, genre_id_list)

        self.insert_film_work()
        self.insert_genre()
        self.insert_person()
        self.insert_person_film_work()
        self.insert_genre_film_work()
