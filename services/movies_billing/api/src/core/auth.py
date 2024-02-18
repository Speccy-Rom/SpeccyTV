import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from core.config import settings

oauth_schema = HTTPBearer()


async def auth(authorization: HTTPAuthorizationCredentials = Depends(oauth_schema)):
    """
    This asynchronous function is used to authenticate a user.

    It decodes the JWT token provided in the authorization header and extracts the user ID from the payload.
    If the user ID is not found in the payload, it raises an HTTP 404 error.
    If the JWT token cannot be decoded, it raises an HTTP 401 error.

    Parameters:
    authorization (HTTPAuthorizationCredentials): The authorization credentials provided in the HTTP header.

    Returns:
    str: The user ID extracted from the JWT token payload.

    Raises:
    HTTPException: An exception of type HTTPException is raised in case of any error.
    """
    try:
        payload = jwt.decode(authorization.credentials,
                             settings.jwt_secret_key,
                             algorithms=[settings.jwt_algorithm])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="User id not found")
        return user_id
    except jwt.exceptions.DecodeError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


def get_auth():
    """
    This function returns the auth function.

    Returns:
    function: The auth function.
    """
    return auth
