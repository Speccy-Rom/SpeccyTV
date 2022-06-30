from http import HTTPStatus
from datetime import datetime

from flask_restful import Resource, reqparse, marshal, fields, Api, url_for
from flask import abort, request, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from flasgger import swag_from

from models.users import User, UserLogin, SocialAccount
from utils.jwt_tokens import generate_tokens
from utils.rate_limiter import limiter
from utils.oauth import oauth
from core import redis, config
from core.db import db

tokens_bp = Blueprint('tokens', __name__)
tokens_api = Api(tokens_bp)


class LoginResource(Resource):
    decorators = [
        limiter.limit('1/second', methods=['POST'])
    ]
    resource_fields = {
        'access_token': fields.String,
        'refresh_token': fields.String,
    }

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('email', required=True)
        self.parser.add_argument('password', required=True)

    @swag_from(config.DOCS_DIR.joinpath('auth').joinpath('login.yml'))
    def post(self):
        data = self.parser.parse_args()
        user = User.query.filter_by(email=data['email']).first()

        if not user or not user.check_password(data['password']):
            return abort(HTTPStatus.CONFLICT)

        new_login = UserLogin(
            ip_address=request.remote_addr,
            time=datetime.now(),
            user=user.id
        )
        db.session.add(new_login)
        db.session.commit()
        access_token, refresh_token = generate_tokens(user=user, user_agent=request.user_agent.string)
        return (
            marshal({'access_token': access_token, 'refresh_token': refresh_token}, self.resource_fields),
            HTTPStatus.OK
        )


class LogoutResource(Resource):
    decorators = [
        limiter.limit('1/second', methods=['DELETE'])
    ]

    @swag_from(config.DOCS_DIR.joinpath('auth').joinpath('logout.yml'))
    @jwt_required()
    def delete(self):
        access_jti = get_jwt()['jti']
        redis.revoke_token(access_jti)
        return {}, HTTPStatus.NO_CONTENT


class LogoutAllResource(Resource):
    decorators = [
        limiter.limit('5/day', methods=['DELETE'])
    ]

    @swag_from(config.DOCS_DIR.joinpath('auth').joinpath('logout_all_accounts.yml'))
    @jwt_required()
    def delete(self):
        user_id = get_jwt_identity()
        redis.delete_user_tokens(user_id)
        return {}, HTTPStatus.NO_CONTENT


class RefreshResource(Resource):
    decorators = [
        limiter.limit('1/minute', methods=['POST'])
    ]
    resource_fields = {
        'access_token': fields.String,
        'refresh_token': fields.String,
    }

    @swag_from(config.DOCS_DIR.joinpath('auth').joinpath('refresh.yml'))
    @jwt_required(refresh=True)
    def post(self):
        refresh_jti = get_jwt()['jti']
        redis.revoke_token(refresh_jti, refresh=True)

        user_id = get_jwt_identity()
        user = User.query.filter_by(id=user_id).first()

        if not user:
            return abort(HTTPStatus.CONFLICT)

        access_token, refresh_token = generate_tokens(user=user, user_agent=request.user_agent.string)
        return (
            marshal({'access_token': access_token, 'refresh_token': refresh_token}, self.resource_fields),
            HTTPStatus.OK
        )


class ValidationResource(Resource):

    @jwt_required()
    def get(self):
        return {'msg': 'Token is valid'}, HTTPStatus.OK


class GoogleLoginResource(Resource):

    @swag_from(config.DOCS_DIR.joinpath('auth').joinpath('google-login.yml'))
    def get(self):
        redirect_uri = url_for('googleauthresource', _external=True)
        return oauth.google.authorize_redirect(redirect_uri)


class GoogleAuthResource(LoginResource):

    @swag_from(config.DOCS_DIR.joinpath('auth').joinpath('google-auth.yml'))
    def post(self):
        oauth_token = oauth.google.authorize_access_token()
        google_user = oauth.google.parse_id_token(oauth_token)

        user = User.query.filter_by(email=google_user.get('email')).first()
        if not user:
            return abort(HTTPStatus.CONFLICT)

        s_account = SocialAccount.query.filter_by(social_id=google_user.get('sub'), social_name='google').first()
        if not s_account:
            acc = SocialAccount(user_id=user.id, social_id=google_user.get('sub'), social_name='google')
            db.session.add(acc)
            db.session.commit()

        access_token, refresh_token = generate_tokens(user=user, user_agent=request.user_agent.string)
        return (
            marshal({'access_token': access_token, 'refresh_token': refresh_token}, self.resource_fields),
            HTTPStatus.OK
        )


tokens_api.add_resource(LoginResource, '/auth/v1/auth_token')
tokens_api.add_resource(LogoutResource, '/auth/v1/auth_token')
tokens_api.add_resource(LogoutAllResource, '/auth/v1/auth_token/all')
tokens_api.add_resource(RefreshResource, '/auth/v1/auth_token/token_refresh')
tokens_api.add_resource(ValidationResource, '/auth/v1/auth_token/validation')
tokens_api.add_resource(GoogleLoginResource, '/auth/v1/auth_token/google_login')
tokens_api.add_resource(GoogleAuthResource, '/auth/v1/auth_token/google_auth')
