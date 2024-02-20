# Importing necessary modules and classes
import logging
from http import HTTPStatus
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from models.genre import BaseGenre, Genre
from queryes.base import QueryParamsBase, ServiceQueryInfo
from queryes.genre import GenreQueryParamsInfo, GenreQueryParamsSearch
from services.genre import GenreService, get_genre_service

# Creating an instance of APIRouter
router = APIRouter()

# Setting up logger for this module
module_logger = logging.getLogger('GenreAPI')


# Function to get genres based on the provided query parameters
async def get_genres(
    params: QueryParamsBase, genre_service: GenreService
) -> List[BaseGenre]:
    """
    This function retrieves genres based on the provided query parameters.

    Args:
        params (QueryParamsBase): The query parameters to filter genres.
        genre_service (GenreService): The service to retrieve genres.

    Returns:
        List[BaseGenre]: A list of genres that match the query parameters.

    Raises:
        HTTPException: If no genres are found, it raises an HTTPException with status code 404.
    """
    module_logger.info('Getting genres with query (%s)', params)
    service_query_info = ServiceQueryInfo.parse_obj(params.asdict())
    genres = await genre_service.get_by_query(service_query_info)
    if not genres:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='genres not found')

    return [Genre(**genre.dict()) for genre in genres]


# Route to get genres with pagination and sorting by name
@router.get(
    '/',
    response_model=List[BaseGenre],
    description='Info about genres with pagination and sorting by name',
    response_description='Genres list with base info',
)
async def genres_info(
    params: GenreQueryParamsInfo = Depends(),
    genre_service: GenreService = Depends(get_genre_service),
) -> List[BaseGenre]:
    """
    This route retrieves genres with pagination and sorting by name.

    Args:
        params (GenreQueryParamsInfo): The query parameters to filter genres.
        genre_service (GenreService): The service to retrieve genres.

    Returns:
        List[BaseGenre]: A list of genres that match the query parameters.
    """
    return await get_genres(params, genre_service)


# Route to perform full-text search on genres with pagination and sorting by name and relevance
@router.get(
    '/search',
    response_model=List[BaseGenre],
    description='Genres full-text search with pagination and sorting by name and relevance',
    response_description='Genres list with base info',
)
async def genres_search(
    params: GenreQueryParamsSearch = Depends(),
    genre_service: GenreService = Depends(get_genre_service),
) -> List[BaseGenre]:
    """
    This route performs a full-text search on genres with pagination and sorting by name and relevance.

    Args:
        params (GenreQueryParamsSearch): The query parameters to filter genres.
        genre_service (GenreService): The service to retrieve genres.

    Returns:
        List[BaseGenre]: A list of genres that match the query parameters.
    """
    return await get_genres(params, genre_service)


# Route to get detailed info about a genre including its description
@router.get(
    '/{genre_id}',
    response_model=Genre,
    description='Detailed info about genre including description',
    response_description='Genre details',
)
async def genre_details(
    genre_id: UUID, genre_service: GenreService = Depends(get_genre_service)
) -> Genre:
    """
    This route retrieves detailed info about a genre including its description.

    Args:
        genre_id (UUID): The id of the genre to retrieve.
        genre_service (GenreService): The service to retrieve genres.

    Returns:
        Genre: The genre that matches the provided id.

    Raises:
        HTTPException: If no genre is found, it raises an HTTPException with status code 404.
    """
    module_logger.info('Getting genre with id (%s)', genre_id)
    genre = await genre_service.get_by_id(str(genre_id))
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='genre not found')

    return Genre(**genre.dict())
