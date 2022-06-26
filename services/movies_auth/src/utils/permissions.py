from functools import wraps
from typing import Union, Optional

from flask import abort
from flask_jwt_extended import get_jwt_identity

from models.users import User


def permissions_required(*permissions: str, condition: Optional[dict] = None):
    """
    A decorator to check user permissions for endpoint.
    If permissions are not satisfied, access to endpoint is denied with 403 code.
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
    """

    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            user_id = get_jwt_identity()
            user = User.query.filter_by(id=user_id).first()
            if not user:
                return abort(409)

            permissions_query = _get_permissions_query(*permissions, condition=condition)
            if not user.check_permissions(permissions_query):
                return abort(403)

            return fn(*args, **kwargs)

        return decorator

    return wrapper


def _get_permissions_query(*permissions: str, condition: Optional[dict]) -> dict:
    permissions_query: dict[str, list[Union[str, dict]]] = {'any': ['all_all']}
    if condition:
        if condition_any := condition.get('any'):
            permissions_query['any'] += condition_any
        else:
            permissions_query['any'].append(condition)
    elif len(permissions) == 1:
        if permissions[0] != 'all_all':
            permissions_query['any'].append(permissions[0])
    elif len(permissions) > 1:
        permissions_query['any'].append({'all': list(permissions)})

    return permissions_query


class PermissionNames:
    ALL_ALL = 'all_all'
    PERMISSIONS_ADMIN = 'permissions_admin'


class RoleNames:
    SUPERUSER = 'superuser'
