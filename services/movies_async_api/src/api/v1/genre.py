import logging
from http import HTTPStatus
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from models.genre import BaseGenre, Genre
from queryes.base import QueryParamsBase, ServiceQueryInfo
from queryes.genre import GenreQueryParamsInfo, GenreQueryParamsSearch
from services.genre import GenreService, get_genre_service

router = APIRouter()

module_logger = logging.getLogger('GenreAPI')


async def get_genres(params: QueryParamsBase, genre_service: GenreService) -> List[BaseGenre]:
    module_logger.info('Getting genres with query (%s)', params)
    service_query_info = ServiceQueryInfo.parse_obj(params.asdict())
    genres = await genre_service.get_by_query(service_query_info)
    if not genres:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='genres not found')

    return [Genre(**genre.dict()) for genre in genres]


@router.get('/',
            response_model=List[BaseGenre],
            description='Info about genres with pagination and sorting by name',
            response_description='Genres list with base info')
async def genres_info(params: GenreQueryParamsInfo = Depends(),
                      genre_service: GenreService = Depends(get_genre_service)) -> List[BaseGenre]:
    genres = await get_genres(params, genre_service)
    return genres


@router.get('/search',
            response_model=List[BaseGenre],
            description='Genres full-text search with pagination and sorting by name and relevance',
            response_description='Genres list with base info')
async def genres_search(params: GenreQueryParamsSearch = Depends(),
                        genre_service: GenreService = Depends(get_genre_service)) -> List[BaseGenre]:
    genres = await get_genres(params, genre_service)
    return genres


@router.get('/{genre_id}',
            response_model=Genre,
            description='Detailed info about genre including description',
            response_description='Genre details')
async def genre_details(genre_id: UUID, genre_service: GenreService = Depends(get_genre_service)) -> Genre:
    module_logger.info('Getting genre with id (%s)', genre_id)
    genre = await genre_service.get_by_id(str(genre_id))
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='genre not found')

    return Genre(**genre.dict())
