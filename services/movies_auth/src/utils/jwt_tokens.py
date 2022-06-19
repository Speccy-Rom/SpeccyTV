from typing import Tuple
from flask import Flask
from flask_jwt_extended import JWTManager, get_jti, create_access_token, create_refresh_token

from core import redis
from core import config

jwt = JWTManager()


@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    token_in_redis = redis.redis_db.get(jti)
    return token_in_redis == b'revoked'


def init_jwt(app: Flask):
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = config.ACCESS_EXPIRES
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = config.REFRESH_EXPIRES
    jwt.init_app(app)


def generate_tokens(user, user_agent: str) -> Tuple[str, str]:
    user_id = str(user.id)
    user_extra = {
        # 'superuser': user.superuser,
        # 'roles': [role.name for role in user.roles],
        'email': user.email
    }
    access_token = create_access_token(identity=user_id, expires_delta=config.ACCESS_EXPIRES,
                                       additional_claims=user_extra)
    refresh_token = create_refresh_token(identity=user_id, expires_delta=config.REFRESH_EXPIRES)
    redis.save_tokens(
        user_id=user_id,
        access_jti=get_jti(access_token),
        refresh_jti=get_jti(refresh_token),
        user_agent=user_agent
    )
    return access_token, refresh_token
