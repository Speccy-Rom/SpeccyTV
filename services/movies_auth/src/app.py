from http import HTTPStatus

from flask import Flask, request
from flask_migrate import Migrate
from flasgger import Swagger
from flask_opentracing import FlaskTracing

from core.config import DOCS_DIR, DATABASE_URI, SECRET_KEY
from core.db import init_db
from core.trace import setup_jaeger
from utils import jwt_tokens, rate_limiter, oauth

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = SECRET_KEY

db = init_db(app)
migrate = Migrate(app, db)

swagger = Swagger()
swagger.config['url_prefix'] = '/auth'
# Currently flasgger's swag_from doesn't work well with flask-restful resources when they are added with several urls,
# so by now we add the whole swagger spec for our service as a template.
swagger.template_file = DOCS_DIR.joinpath('Auth_OpenAPI_spec.yml').as_posix()
swagger.init_app(app)

jwt_tokens.init_jwt(app)
rate_limiter.init_limiter(app)
oauth.init_oauth(app)

errors = {
    'sqlalchemy.exc.IntegrityError': {
        'message': 'Email already exists',
        'status': HTTPStatus.CONFLICT.value,
    },
    'IntegrityError': {
        'message': 'Email already exists',
        'status': HTTPStatus.CONFLICT.value,
    },
}

tracer = FlaskTracing(setup_jaeger, True, app=app)


@app.before_request
def before_request():
    request_id = request.headers.get('X-Request-Id')

    if not request_id:
        raise RuntimeError('request id is requred')


def create_app():
    from api.v1 import users, permissions, auth_token
    app.register_blueprint(users.users_bp)
    app.register_blueprint(permissions.permissions_bp)
    app.register_blueprint(auth_token.tokens_bp)


def main():
    create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)


import cli
# В какой-то момент эти импорты потребовались для нормальной работы alembic'а.
from models import *

if __name__ == '__main__':
    main()
