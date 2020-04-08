from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_app(app):
    for extension in [db]:
        extension.init_app(app)
