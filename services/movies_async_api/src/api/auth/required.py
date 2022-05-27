import json
from typing import Union, Optional

import jwt
from aiohttp.client_exceptions import ClientConnectorError
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN

from api.utils.http_client import HTTPClient, http_client
from core.config import AUTH_TOKEN_VALIDATION_URL, AUTH_PERMISSIONS_AND_TOKEN_VALIDATION_URL


class AuthInfo(BaseModel):
    user_id: str
    token_valid: Optional[bool] = None
    permissions_valid: Optional[bool] = None


class AuthRequired:
    """
        A tool (a dependency class) to validate user authentication and permission for endpoint via Auth service.
        Depending on parameters, it validates token, permissions (if any) and based on that can prevent access
        to an endpoint with corresponding http status codes and messages if needed, or it can provide access and
        just provide auth info on whether token/permissions are valid or not if corresponding options are enabled.
        If permissions are not satisfied, access to endpoint is denied with 403 code in strict mode. Or provided
        with permissions_valid set to false.
        One can specify any number of permissions or a condition for more sophisticated requirements.
        When several permissions are specified, all of them are supposed to be required.
        Whatever condition or permissions are specified, superuser permission 'any_any' is always implicitly
        added as alternative requirement, which means any permissions requirement is satisfied for superuser.
        :param permissions:
            Required permissions. If several permissions are specified, all of them are supposed to be required.
        :param condition:
            Condition on required permissions. It is supposed to be used as an alternative to permissions args for
            sophisticated cases. When condition is specified, permissions args are not considered.
            Examples:
                {'any': ['perm_1', 'perm_2', 'perm_3']}
                {'any': ['perm_1', {'all': ['perm_2', 'perm_3']}]}
        :param token_optional
            If True, token is not strictly required. In this case, access to the endpoint will be provided both for
            requests with valid token and without token at all. In case token is provided, but is invalid, access will
            still be denied with 401 code.
        :param permissions_optional
            If True, permissions are not strictly required to access an endpoint. An info on whether permissions are
            valid or not are provided in permissions_valid field of auth info.
        """
    _http_bearer = HTTPBearer(auto_error=False)

    def __init__(
            self, *permissions: str, condition: Optional[dict] = None, token_optional=True, permissions_optional=True):
        self.permissions = permissions
        self.condition = condition
        self.token_optional = token_optional
        self.permissions_optional = permissions_optional

    async def __call__(self, request: Request,
                       bearer_info: HTTPAuthorizationCredentials = Depends(_http_bearer),
                       client: HTTPClient = Depends(http_client)):
        if not bearer_info or not bearer_info.credentials:
            if not self.token_optional:
                raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Authorization header is missing")
            else:
                return None

        token = bearer_info.credentials
        user_id = jwt.decode(token, options={'verify_signature': False})['sub']
        auth_info = AuthInfo(user_id=user_id)

        check_token_only = not self.permissions and not self.condition
        if check_token_only:
            url = AUTH_TOKEN_VALIDATION_URL
            params = None
        else:
            url = AUTH_PERMISSIONS_AND_TOKEN_VALIDATION_URL.format(user_id=user_id)
            params = {'permissions': json.dumps(self._get_permissions_query())}

        try:
            auth_response = await client.get(url, params=params, token=token)
        except ClientConnectorError:
            # graceful degradation
            return auth_info

        token_valid = auth_response.status == 200
        if not token_valid:
            msg = auth_response.json.get('msg')
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail=msg)
        auth_info.token_valid = token_valid

        if check_token_only:
            return auth_info

        permissions_valid = token_valid and auth_response.json.get('valid')
        if not permissions_valid and not self.permissions_optional:
            raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail='No permissions')
        auth_info.permissions_valid = permissions_valid

        return auth_info

    def _get_permissions_query(self) -> dict:
        permissions_query: dict[str, list[Union[str, dict]]] = {'any': ['all_all']}
        if self.condition:
            if condition_any := self.condition.get('any'):
                permissions_query['any'] += condition_any
            else:
                permissions_query['any'].append(self.condition)
        elif len(self.permissions) == 1:
            if self.permissions[0] != 'all_all':
                permissions_query['any'].append(self.permissions[0])
        elif len(self.permissions) > 1:
            permissions_query['any'].append({'all': list(self.permissions)})

        return permissions_query
