import logging
from http import HTTPStatus
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from models.film import BaseFilm, Film
from queryes.base import QueryParamsBase, ServiceQueryInfo
from queryes.film import FilmQueryParamsInfo, FilmQueryParamsSearch
from services.film import FilmService, get_film_service

# Initialize the API router
router = APIRouter()

# Set up logging for this module
module_logger = logging.getLogger('FilmAPI')


# Function to get films based on query parameters
async def get_films(params: QueryParamsBase, film_service: FilmService) -> List[BaseFilm]:
    """
    This function retrieves a list of films based on the provided query parameters.

    :param params: Query parameters for retrieving films
    :param film_service: Service for interacting with the film data
    :return: List of films
    """
    module_logger.info('Getting films with query (%s)', params)
    service_query_info = ServiceQueryInfo.parse_obj(params.asdict())
    films = await film_service.get_by_query(service_query_info)
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='films not found')

    return [Film(**film.dict()) for film in films]


# API endpoint for getting films with pagination, filtering by genre and sorting by rating and title
@router.get('/',
            response_model=List[BaseFilm],
            description='Info about films with pagination, filtering by genre and sorting by rating and title',
            response_description='Films list with base info')
async def films_info(params: FilmQueryParamsInfo = Depends(),
                     film_service: FilmService = Depends(get_film_service)) -> List[BaseFilm]:
    """
    This endpoint retrieves a list of films with pagination, filtering by genre and sorting by rating and title.

    :param params: Query parameters for retrieving films
    :param film_service: Service for interacting with the film data
    :return: List of films
    """
    return await get_films(params, film_service)


# API endpoint for full-text search of films with pagination, filtering by genre and sorting by rating, title, and relevance
@router.get('/search',
            response_model=List[BaseFilm],
            description='''Films full-text search with pagination, filtering by genre and sorting by rating, title,
                        and relevance''',
            response_description='Films list with base info')
async def films_search(params: FilmQueryParamsSearch = Depends(),
                       film_service: FilmService = Depends(get_film_service)) -> List[BaseFilm]:
    """
    This endpoint performs a full-text search of films with pagination, filtering by genre and sorting by rating, title, and relevance.

    :param params: Query parameters for retrieving films
    :param film_service: Service for interacting with the film data
    :return: List of films
    """
    return await get_films(params, film_service)


# API endpoint for getting detailed info about a specific film
@router.get('/{film_id}',
            response_model=Film,
            description='Detailed info about film including description, rating, genres, persons etc',
            response_description='Film details')
async def film_details(film_id: UUID, film_service: FilmService = Depends(get_film_service)) -> Film:
    """
    This endpoint retrieves detailed information about a specific film.

    :param film_id: The UUID of the film to retrieve
    :param film_service: Service for interacting with the film data
    :return: Detailed information about the film
    """
    module_logger.info('Getting film with id (%s)', film_id)
    film = await film_service.get_by_id(str(film_id))
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='film not found')

    return Film(**film.dict())
