import json
from datetime import timedelta
from typing import Optional, Type
from urllib import parse
from http import HTTPStatus

from flask_jwt_extended import jwt_required
from flask_restful import Resource, reqparse, marshal, fields, Api
from flask import abort, Blueprint
import sqlalchemy

from utils.rate_limiter import limiter
from core.db import db
from models.permission import Permission, Role
from models.users import User
from utils.permissions import permissions_required, PermissionNames
from utils.cache.base import cache

permissions_bp = Blueprint('permissions', __name__)
permissions_api = Api(permissions_bp)


class BaseResource(Resource):
    @staticmethod
    def get_object(model: Type[db.Model], **required_fields) -> Optional[db.Model]:
        try:
            if obj := model.query.filter_by(**required_fields).first():
                return obj
        except sqlalchemy.exc.DataError:
            return abort(HTTPStatus.BAD_REQUEST)

        return abort(HTTPStatus.NOT_FOUND)


class UserPermissionResource(Resource):
    decorators = [
        limiter.limit('1/second', methods=['GET']),
        limiter.limit('5/day', methods=['POST', 'DELETE'])
    ]

    resource_fields = {
        'uuid': fields.String(attribute='id'),
        'name': fields.String,
        'description': fields.String
    }

    user_resource_fields = {
        'uuid': fields.String(attribute='id'),
        'email': fields.String,
        'first_name': fields.String,
        'last_name': fields.String,
        'permissions': fields.List(fields.Nested(resource_fields), attribute=lambda user: user.permissions.all())
    }

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('name', required=True)

    @staticmethod
    def get_object(model: Type[db.Model], **required_fields) -> Optional[db.Model]:
        try:
            if obj := model.query.filter_by(**required_fields).first():
                return obj
        except sqlalchemy.exc.DataError:
            return abort(HTTPStatus.BAD_REQUEST)

        return abort(HTTPStatus.NOT_FOUND)

    @jwt_required()
    @permissions_required(PermissionNames.PERMISSIONS_ADMIN)
    def get(self, user_id: str):
        user = self.get_object(User, id=user_id)
        return marshal(user.permissions.all(), self.resource_fields), HTTPStatus.OK

    @jwt_required()
    @permissions_required(PermissionNames.PERMISSIONS_ADMIN)
    def post(self, user_id: str):
        user = self.get_object(User, id=user_id)
        permission_data = self.parser.parse_args()
        permission_name = permission_data['name']
        permission = self.get_object(Permission, name=permission_name)
        user.add_permission(permission)

        try:
            db.session.commit()
        except sqlalchemy.exc.IntegrityError:
            return abort(HTTPStatus.CONFLICT)

        return marshal(user, self.user_resource_fields), HTTPStatus.OK

    @jwt_required()
    @permissions_required(PermissionNames.PERMISSIONS_ADMIN)
    def delete(self, user_id: str, permission_name: str):
        user = self.get_object(User, id=user_id)
        permission = self.get_object(Permission, name=permission_name)
        user.remove_permission(permission)
        db.session.commit()
        return marshal(user, self.user_resource_fields), HTTPStatus.OK


PERMISSION_FIELDS = {
    'uuid': fields.String(attribute='id'),
    'name': fields.String,
    'description': fields.String
}

ROLE_FIELDS = {
    'uuid': fields.String(attribute='id'),
    'name': fields.String,
    'description': fields.String,
    'permissions': fields.List(fields.Nested(PERMISSION_FIELDS),
                               attribute=lambda role: role.permissions.all())
}


class BaseCombinedPermissionResource(BaseResource):
    @cache(key_suffix='combined_permissions', expires=timedelta(minutes=60))
    def _get_combined_permissions(self, user_id):
        user = self.get_object(User, id=user_id)
        return marshal(user.combined_permissions, PERMISSION_FIELDS)


class UserCombinedPermissionResource(BaseCombinedPermissionResource):
    @jwt_required()
    def get(self, user_id: str):
        combined_permissions = self._get_combined_permissions(user_id)
        return combined_permissions, HTTPStatus.OK


class UserPermissionValidationResource(BaseCombinedPermissionResource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('permissions', location='args', required=True)

    # e.g. curl ...  --data-urlencode 'permissions={"any":["packs_ext", {"all": ["cloud_people", "electric_edwards"]}]}'
    @jwt_required()
    def get(self, user_id: str):
        combined_permissions = self._get_combined_permissions(user_id)
        combined_permissions_set = {permission['name'] for permission in combined_permissions}
        query_data = self.parser.parse_args()
        permissions_query_str = parse.unquote(query_data['permissions'])
        permissions_query = json.loads(permissions_query_str)
        return {'valid': User.check_permissions_set(permissions_query, combined_permissions_set)}, HTTPStatus.OK


class UserRoleResource(BaseResource):
    resource_fields = ROLE_FIELDS

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('name', required=True)

    @jwt_required()
    @permissions_required(PermissionNames.PERMISSIONS_ADMIN)
    def get(self, user_id: str):
        user = self.get_object(User, id=user_id)
        return marshal(user.roles.all(), self.resource_fields), HTTPStatus.OK

    @jwt_required()
    @permissions_required(PermissionNames.PERMISSIONS_ADMIN)
    def post(self, user_id: str):
        user = self.get_object(User, id=user_id)
        role_data = self.parser.parse_args()
        role_name = role_data['name']
        role = self.get_object(Role, name=role_name)
        user.add_role(role)

        try:
            db.session.commit()
        except sqlalchemy.exc.IntegrityError:
            return abort(HTTPStatus.CONFLICT)

        return marshal(user.roles.all(), self.resource_fields), HTTPStatus.OK

    @jwt_required()
    @permissions_required(PermissionNames.PERMISSIONS_ADMIN)
    def delete(self, user_id: str, role_name: str):
        user = self.get_object(User, id=user_id)
        role = self.get_object(Role, name=role_name)
        user.remove_role(role)
        db.session.commit()
        return marshal(user.roles.all(), self.resource_fields), HTTPStatus.OK


class RolePermissionResource(BaseResource):
    permission_resource_fields = PERMISSION_FIELDS

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('name', required=True)

    @jwt_required()
    @permissions_required(PermissionNames.PERMISSIONS_ADMIN)
    def post(self, role_name: str):
        role = self.get_object(Role, name=role_name)
        permission_data = self.parser.parse_args()
        permission_name = permission_data['name']
        permission = self.get_object(Permission, name=permission_name)
        role.add_permission(permission)

        try:
            db.session.commit()
        except sqlalchemy.exc.IntegrityError:
            return abort(HTTPStatus.CONFLICT)

        return marshal(role.permissions.all(), self.permission_resource_fields), HTTPStatus.OK

    @jwt_required()
    @permissions_required(PermissionNames.PERMISSIONS_ADMIN)
    def delete(self, role_name: str, permission_name: str):
        role = self.get_object(Role, name=role_name)
        permission = self.get_object(Permission, name=permission_name)
        role.remove_permission(permission)
        db.session.commit()
        return marshal(role.permissions.all(), self.permission_resource_fields), HTTPStatus.OK


class RoleResource(BaseResource):
    resource_fields = ROLE_FIELDS

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('name', required=True)
        self.parser.add_argument('description')

        self.patch_parser = reqparse.RequestParser()
        self.patch_parser.add_argument('name', required=False, store_missing=False)
        self.patch_parser.add_argument('description', required=False, store_missing=False)

    @jwt_required()
    @permissions_required(PermissionNames.PERMISSIONS_ADMIN)
    def get(self, role_name=None):
        if not role_name:
            data = Role.query.all()
        else:
            data = self.get_object(Role, name=role_name)
        return marshal(data, self.resource_fields), HTTPStatus.OK

    @jwt_required()
    @permissions_required(PermissionNames.PERMISSIONS_ADMIN)
    def post(self):
        role_data = self.parser.parse_args()
        new_role = Role(**role_data)
        db.session.add(new_role)

        try:
            db.session.commit()
        except sqlalchemy.exc.IntegrityError:
            return abort(HTTPStatus.CONFLICT)

        return marshal(new_role, self.resource_fields), HTTPStatus.CREATED

    @jwt_required()
    @permissions_required(PermissionNames.PERMISSIONS_ADMIN)
    def patch(self, role_name: str):
        role = self.get_object(Role, name=role_name)
        role_patch_data = self.patch_parser.parse_args()
        for name, value in role_patch_data.items():
            setattr(role, name, value)

        try:
            db.session.commit()
        except sqlalchemy.exc.IntegrityError:
            return abort(HTTPStatus.CONFLICT)

        return marshal(role, self.resource_fields)

    @jwt_required()
    @permissions_required(PermissionNames.PERMISSIONS_ADMIN)
    def delete(self, role_name: str):
        role = self.get_object(Role, name=role_name)
        db.session.delete(role)
        db.session.commit()
        return {}, HTTPStatus.NO_CONTENT


class PermissionResource(Resource):
    resource_fields = {
        'uuid': fields.String(attribute='id'),
        'name': fields.String,
        'description': fields.String
    }

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('name', required=True)
        self.parser.add_argument('description')

        self.patch_parser = self.parser.copy()
        self.patch_parser.remove_argument('name')

    @staticmethod
    def get_object(permission_name: str) -> Optional[Permission]:
        try:
            if permission := Permission.query.filter_by(name=permission_name).first():
                return permission
        except sqlalchemy.exc.DataError:
            return abort(HTTPStatus.BAD_REQUEST)

        return abort(HTTPStatus.NOT_FOUND)

    @jwt_required()
    @permissions_required(PermissionNames.PERMISSIONS_ADMIN)
    def get(self):
        permissions = Permission.query.all()
        return marshal(permissions, self.resource_fields), HTTPStatus.OK

    @jwt_required()
    @permissions_required(PermissionNames.PERMISSIONS_ADMIN)
    def post(self):
        permission_data = self.parser.parse_args()
        new_permission = Permission(**permission_data)
        db.session.add(new_permission)

        try:
            db.session.commit()
        except sqlalchemy.exc.IntegrityError:
            return abort(HTTPStatus.CONFLICT)

        return marshal(new_permission, self.resource_fields), HTTPStatus.CREATED

    @jwt_required()
    @permissions_required(PermissionNames.PERMISSIONS_ADMIN)
    def patch(self, permission_name: str):
        permission = self.get_object(permission_name)
        permission_patch_data = self.patch_parser.parse_args()
        for name, value in permission_patch_data.items():
            setattr(permission, name, value)
        db.session.commit()

        return marshal(permission, self.resource_fields)

    @jwt_required()
    @permissions_required(PermissionNames.PERMISSIONS_ADMIN)
    def delete(self, permission_name: str):
        permission = self.get_object(permission_name)
        db.session.delete(permission)
        db.session.commit()
        return {}, HTTPStatus.NO_CONTENT


permissions_api.add_resource(PermissionResource,
                             '/auth/v1/permissions',
                             '/auth/v1/permissions/<string:permission_name>')
permissions_api.add_resource(UserPermissionResource,
                             '/auth/v1/users/<string:user_id>/permissions',
                             '/auth/v1/users/<string:user_id>/permissions/<string:permission_name>')
permissions_api.add_resource(RoleResource,
                             '/auth/v1/roles',
                             '/auth/v1/roles/<string:role_name>')
permissions_api.add_resource(RolePermissionResource,
                             '/auth/v1/roles/<string:role_name>/permissions',
                             '/auth/v1/roles/<string:role_name>/permissions/<string:permission_name>')
permissions_api.add_resource(UserRoleResource,
                             '/auth/v1/users/<string:user_id>/roles',
                             '/auth/v1/users/<string:user_id>/roles/<string:role_name>')
permissions_api.add_resource(UserCombinedPermissionResource,
                             '/auth/v1/users/<string:user_id>/combined_permissions')
permissions_api.add_resource(UserPermissionValidationResource,
                             '/auth/v1/users/<string:user_id>/combined_permissions/validation')
