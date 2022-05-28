import logging
from http import HTTPStatus
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from models.person import BasePerson, Person
from queryes.base import QueryParamsBase, ServiceQueryInfo
from queryes.person import PersonQueryParamsInfo, PersonQueryParamsSearch
from services.person import PersonService, get_person_service

router = APIRouter()

module_logger = logging.getLogger('PersonAPI')


async def get_persons(params: QueryParamsBase, person_service: PersonService) -> List[BasePerson]:
    module_logger.info('Getting persons with query (%s)', params)
    service_query_info = ServiceQueryInfo.parse_obj(params.asdict())
    persons = await person_service.get_by_query(service_query_info)
    if not persons:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='persons not found')

    return [Person(**person.dict()) for person in persons]


@router.get('/',
            response_model=List[BasePerson],
            description='Info about persons with pagination, filtering by film and sorting by full name',
            response_description='Persons list with base info')
async def persons_info(params: PersonQueryParamsInfo = Depends(),
                       person_service: PersonService = Depends(get_person_service)) -> List[BasePerson]:
    persons = await get_persons(params, person_service)
    return persons


@router.get('/search',
            response_model=List[BasePerson],
            description='''Persons full-text search with pagination, filtering by film and sorting by full name 
                        and relevance''',
            response_description='Persons list with base info'
            )
async def persons_search(params: PersonQueryParamsSearch = Depends(),
                         person_service: PersonService = Depends(get_person_service)) -> List[BasePerson]:
    persons = await get_persons(params, person_service)
    return persons


@router.get('/{person_id}',
            response_model=Person,
            description='Detailed info about person including its roles and films',
            response_description='Person details')
async def person_details(person_id: UUID, person_service: PersonService = Depends(get_person_service)) -> Person:
    module_logger.info('Getting person with id (%s)', person_id)
    person = await person_service.get_by_id(str(person_id))
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='person not found')

    return Person(**person.dict())
