films_es_to_api_mapping = {
    'id': 'uuid',
    'rating': 'imdb_rating',
}

persons_es_to_api_mapping = {
    'id': 'uuid',
    'name': 'full_name',
}

genres_es_to_api_mapping = {
    'id': 'uuid',
}


def get_translated_dict(mapping: dict, dictionary: dict) -> dict:
    return {mapping.get(k, k): v for k, v in dictionary.items()}
