from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_db(app):
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://<username>:<password>@<host>/<database_name>'
    db.init_app(app)
    return db
