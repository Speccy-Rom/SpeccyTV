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
    """
    This class represents the login resource for the API. It extends the Resource class from flask_restful.
    It provides the functionality for logging in a user.
    """

    # Decorators for rate limiting the POST requests to 1 per second
    decorators = [
        limiter.limit('1/second', methods=['POST'])
    ]

    # Fields to be returned in the response
    resource_fields = {
        'access_token': fields.String,
        'refresh_token': fields.String,
    }

    def __init__(self):
        """
        Constructor for the LoginResource class. Initializes the request parser and adds the required arguments.
        """
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('email', required=True)
        self.parser.add_argument('password', required=True)

    @swag_from(config.DOCS_DIR.joinpath('auth').joinpath('login.yml'))
    def post(self):
        """
        Handles the POST request for the login resource. It parses the request arguments, checks the user credentials,
        logs the login attempt, and returns the access and refresh tokens if the login is successful.
        """
        data = self.parser.parse_args()
        user = User.query.filter_by(email=data['email']).first()

        # If the user does not exist or the password is incorrect, return a conflict status
        if not user or not user.check_password(data['password']):
            return abort(HTTPStatus.CONFLICT)

        # Log the login attempt
        new_login = UserLogin(
            ip_address=request.remote_addr,
            time=datetime.now(),
            user=user.id
        )
        db.session.add(new_login)
        db.session.commit()

        # Generate the access and refresh tokens
        access_token, refresh_token = generate_tokens(user=user, user_agent=request.user_agent.string)

        # Return the tokens in the response
        return (
            marshal({'access_token': access_token, 'refresh_token': refresh_token}, self.resource_fields),
            HTTPStatus.OK
        )


class LogoutResource(Resource):
    """
    This class represents the logout resource for the API. It extends the Resource class from flask_restful.
    It provides the functionality for logging out a user.
    """

    # Decorators for rate limiting the DELETE requests to 1 per second
    decorators = [
        limiter.limit('1/second', methods=['DELETE'])
    ]

    @swag_from(config.DOCS_DIR.joinpath('auth').joinpath('logout.yml'))
    @jwt_required()
    def delete(self):
        """
        Handles the DELETE request for the logout resource. It revokes the access token of the current user.
        """
        access_jti = get_jwt()['jti']
        redis.revoke_token(access_jti)
        return {}, HTTPStatus.NO_CONTENT


class LogoutAllResource(Resource):
    """
    This class represents the logout all resource for the API. It extends the Resource class from flask_restful.
    It provides the functionality for logging out a user from all devices.
    """

    # Decorators for rate limiting the DELETE requests to 5 per day
    decorators = [
        limiter.limit('5/day', methods=['DELETE'])
    ]

    @swag_from(config.DOCS_DIR.joinpath('auth').joinpath('logout_all_accounts.yml'))
    @jwt_required()
    def delete(self):
        """
        Handles the DELETE request for the logout all resource. It deletes all tokens of the current user.
        """
        user_id = get_jwt_identity()
        redis.delete_user_tokens(user_id)
        return {}, HTTPStatus.NO_CONTENT


class RefreshResource(Resource):
    """
    This class represents the refresh resource for the API. It extends the Resource class from flask_restful.
    It provides the functionality for refreshing the access token of a user.
    """

    # Decorators for rate limiting the POST requests to 1 per minute
    decorators = [
        limiter.limit('1/minute', methods=['POST'])
    ]

    # Fields to be returned in the response
    resource_fields = {
        'access_token': fields.String,
        'refresh_token': fields.String,
    }

    @swag_from(config.DOCS_DIR.joinpath('auth').joinpath('refresh.yml'))
    @jwt_required(refresh=True)
    def post(self):
        """
        Handles the POST request for the refresh resource. It revokes the current refresh token and generates new access and refresh tokens.
        """
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
    """
    This class represents the validation resource for the API. It extends the Resource class from flask_restful.
    It provides the functionality for validating a token.
    """

    @jwt_required()
    def get(self):
        """
        Handles the GET request for the validation resource. It validates the token of the current user.
        """
        return {'msg': 'Token is valid'}, HTTPStatus.OK


class GoogleLoginResource(Resource):
    """
    This class represents the Google login resource for the API. It extends the Resource class from flask_restful.
    It provides the functionality for logging in a user via Google.
    """

    @swag_from(config.DOCS_DIR.joinpath('auth').joinpath('google-login.yml'))
    def get(self):
        """
        Handles the GET request for the Google login resource. It redirects the user to the Google authorization page.
        """
        redirect_uri = url_for('googleauthresource', _external=True)
        return oauth.google.authorize_redirect(redirect_uri)


class GoogleAuthResource(LoginResource):
    """
    This class represents the Google auth resource for the API. It extends the LoginResource class.
    It provides the functionality for authenticating a user via Google.
    """

    @swag_from(config.DOCS_DIR.joinpath('auth').joinpath('google-auth.yml'))
    def post(self):
        """
        Handles the POST request for the Google auth resource. It authorizes the access token from Google, gets the user info from Google,
        checks if the user exists in the database, and if the user exists, it generates new access and refresh tokens.
        """
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
