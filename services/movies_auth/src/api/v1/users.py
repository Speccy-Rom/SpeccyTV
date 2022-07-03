from http import HTTPStatus
import typing

from flask_restful import Resource, reqparse, marshal, fields, Api
from flask_jwt_extended import jwt_required
from flask import abort, Blueprint
import sqlalchemy

from utils.rate_limiter import limiter
from core.db import db
from models.users import User

users_bp = Blueprint('users', __name__)
users_api = Api(users_bp)


class UserResource(Resource):
    decorators = [
        limiter.limit('1/second', methods=['GET']),
        limiter.limit('5/day', methods=['POST', 'PATCH', 'DELETE'])
    ]
    resource_fields = {
        'email': fields.String,
        'first_name': fields.String,
        'last_name': fields.String,
        'uuid': fields.String(attribute='id')
    }

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('email', required=True)
        self.parser.add_argument('first_name')
        self.parser.add_argument('last_name')
        self.parser.add_argument('password', required=True)

        self.patch_parser = reqparse.RequestParser()
        self.patch_parser.add_argument('email')
        self.patch_parser.add_argument('first_name')
        self.patch_parser.add_argument('last_name')

    @staticmethod
    def get_object(user_id: str) -> typing.Optional[User]:
        try:
            if user := User.query.filter_by(id=user_id).first():
                return user
        except sqlalchemy.exc.DataError:
            return abort(HTTPStatus.BAD_REQUEST)

        return abort(HTTPStatus.NOT_FOUND)

    @jwt_required()
    def get(self, user_id: str):
        user = self.get_object(user_id)
        return marshal(user, self.resource_fields)

    def post(self):
        user_data = self.parser.parse_args()
        # since we introduced Users table partitioning by id hash, we can't have unique constraint
        # on email for the whole table anymore, so here we must explicitly check first if user
        # with such email already exists
        existing_user = User.query.filter_by(email=user_data['email']).first()
        if existing_user:
            return abort(HTTPStatus.CONFLICT)
        new_user = User(**user_data)
        db.session.add(new_user)

        try:
            db.session.commit()
        except sqlalchemy.exc.IntegrityError:
            return abort(HTTPStatus.CONFLICT)

        return marshal(new_user, self.resource_fields), HTTPStatus.CREATED

    @jwt_required()
    def patch(self, user_id):
        user = self.get_object(user_id)
        user_data = self.patch_parser.parse_args()
        for name, value in user_data.items():
            if not value:
                continue

            if name == 'email':
                user.email = value
            elif name == 'first_name':
                user.first_name = value
            elif name == 'last_name':
                user.last_name = value

        db.session.commit()
        return marshal(user, self.resource_fields)

    @jwt_required()
    def delete(self, user_id):
        user = self.get_object(user_id)
        db.session.delete(user)
        db.session.commit()
        return {}, HTTPStatus.NO_CONTENT


class UserPasswordResource(Resource):
    decorators = [
        limiter.limit('5/day', methods=['POST'])
    ]

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('new_password', required=True)
        self.parser.add_argument('old_password', required=True)

    @jwt_required()
    def post(self, user_id: str):
        user = UserResource.get_object(user_id)
        passwords = self.parser.parse_args()
        if not user.check_password(passwords['old_password']):
            return abort(HTTPStatus.BAD_REQUEST)

        user.set_password(passwords['new_password'])
        db.session.commit()
        return marshal(user, UserResource.resource_fields), HTTPStatus.OK


class UserLoginResource(Resource):
    user_login = {
        'uuid': fields.String(attribute='id'),
        'ip_address': fields.String,
        'time': fields.DateTime,
    }

    user_logins_list = {
        'logins': fields.List(fields.Nested(user_login)),
    }

    @jwt_required()
    def get(self, user_id: str):
        user = UserResource.get_object(user_id)
        return marshal(user, self.user_logins_list), HTTPStatus.OK


users_api.add_resource(UserResource, '/auth/v1/users', '/auth/v1/users/<string:user_id>')
users_api.add_resource(UserPasswordResource, '/auth/v1/users/<string:user_id>/password')
users_api.add_resource(UserLoginResource, '/auth/v1/users/<string:user_id>/logins')
