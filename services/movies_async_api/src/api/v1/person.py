# Importing necessary modules and classes
import logging
from http import HTTPStatus
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from models.person import BasePerson, Person
from queryes.base import QueryParamsBase, ServiceQueryInfo
from queryes.person import PersonQueryParamsInfo, PersonQueryParamsSearch
from services.person import PersonService, get_person_service

# Creating an instance of APIRouter
router = APIRouter()

# Setting up logger for this module
module_logger = logging.getLogger('PersonAPI')


# Function to get persons based on the provided query parameters
async def get_persons(
    params: QueryParamsBase, person_service: PersonService
) -> List[BasePerson]:
    """
    This function retrieves persons based on the provided query parameters.

    Args:
        params (QueryParamsBase): The query parameters to filter persons.
        person_service (PersonService): The service to retrieve persons.

    Returns:
        List[BasePerson]: A list of persons that match the query parameters.

    Raises:
        HTTPException: If no persons are found, it raises an HTTPException with status code 404.
    """
    module_logger.info('Getting persons with query (%s)', params)
    service_query_info = ServiceQueryInfo.parse_obj(params.asdict())
    persons = await person_service.get_by_query(service_query_info)
    if not persons:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='persons not found'
        )

    return [Person(**person.dict()) for person in persons]


# Route to get persons with pagination, filtering by film and sorting by full name
@router.get(
    '/',
    response_model=List[BasePerson],
    description='Info about persons with pagination, filtering by film and sorting by full name',
    response_description='Persons list with base info',
)
async def persons_info(
    params: PersonQueryParamsInfo = Depends(),
    person_service: PersonService = Depends(get_person_service),
) -> List[BasePerson]:
    """
    This route retrieves persons with pagination, filtering by film and sorting by full name.

    Args:
        params (PersonQueryParamsInfo): The query parameters to filter persons.
        person_service (PersonService): The service to retrieve persons.

    Returns:
        List[BasePerson]: A list of persons that match the query parameters.
    """
    return await get_persons(params, person_service)


# Route to perform full-text search on persons with pagination, filtering by film and sorting by full name and relevance
@router.get(
    '/search',
    response_model=List[BasePerson],
    description='''Persons full-text search with pagination, filtering by film and sorting by full name
                        and relevance''',
    response_description='Persons list with base info',
)
async def persons_search(
    params: PersonQueryParamsSearch = Depends(),
    person_service: PersonService = Depends(get_person_service),
) -> List[BasePerson]:
    """
    This route performs a full-text search on persons with pagination, filtering by film and sorting by full name and relevance.

    Args:
        params (PersonQueryParamsSearch): The query parameters to filter persons.
        person_service (PersonService): The service to retrieve persons.

    Returns:
        List[BasePerson]: A list of persons that match the query parameters.
    """
    return await get_persons(params, person_service)


# Route to get detailed info about a person including its roles and films
@router.get(
    '/{person_id}',
    response_model=Person,
    description='Detailed info about person including its roles and films',
    response_description='Person details',
)
async def person_details(
    person_id: UUID, person_service: PersonService = Depends(get_person_service)
) -> Person:
    """
    This route retrieves detailed info about a person including its roles and films.

    Args:
        person_id (UUID): The id of the person to retrieve.
        person_service (PersonService): The service to retrieve persons.

    Returns:
        Person: The person that matches the provided id.

    Raises:
        HTTPException: If no person is found, it raises an HTTPException with status code 404.
    """
    module_logger.info('Getting person with id (%s)', person_id)
    person = await person_service.get_by_id(str(person_id))
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='person not found')

    return Person(**person.dict())
