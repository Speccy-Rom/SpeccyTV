from typing import Tuple
from flask import Flask
from flask_jwt_extended import (
    JWTManager,
    get_jti,
    create_access_token,
    create_refresh_token,
)

from core import redis
from core import config

# Initialize the JWTManager
jwt = JWTManager()


@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload):
    """
    Check if a JWT token is revoked.

    This function checks if a JWT token is revoked by looking up the token's JTI
    in Redis. If the token is found and its value is 'revoked', the function returns True.

    Args:
        jwt_header: The header of the JWT token.
        jwt_payload: The payload of the JWT token.

    Returns:
        bool: True if the token is revoked, False otherwise.
    """
    jti = jwt_payload["jti"]
    token_in_redis = redis.redis_db.get(jti)
    return token_in_redis == b'revoked'


def init_jwt(app: Flask):
    """
    Initialize the JWTManager with the application's configuration.

    This function sets up the JWTManager by configuring it with the settings
    defined in the application's configuration. The settings include the access token
    expiry time and the refresh token expiry time.

    Args:
        app (Flask): The Flask application to initialize the JWTManager for.
    """
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = config.ACCESS_EXPIRES
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = config.REFRESH_EXPIRES
    jwt.init_app(app)


def generate_tokens(user, user_agent: str) -> Tuple[str, str]:
    """
    Generate access and refresh tokens for a user.

    This function generates an access token and a refresh token for a user, and saves
    the tokens' JTIs in Redis. The tokens include the user's ID and email as additional claims.

    Args:
        user: The user for whom to generate the tokens.
        user_agent (str): The user agent string of the client making the request.

    Returns:
        Tuple[str, str]: The generated access token and refresh token.
    """
    user_id = str(user.id)
    user_extra = {
        # 'superuser': user.superuser,
        # 'roles': [role.name for role in user.roles],
        'email': user.email
    }
    access_token = create_access_token(
        identity=user_id,
        expires_delta=config.ACCESS_EXPIRES,
        additional_claims=user_extra,
    )
    refresh_token = create_refresh_token(
        identity=user_id, expires_delta=config.REFRESH_EXPIRES
    )
    redis.save_tokens(
        user_id=user_id,
        access_jti=get_jti(access_token),
        refresh_jti=get_jti(refresh_token),
        user_agent=user_agent,
    )
    return access_token, refresh_token
