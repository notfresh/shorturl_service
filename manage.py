# -*- coding:utf-8 -*-
from flask import current_app
from datetime import datetime, timedelta
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand
from sqlalchemy import func
from app import create_app
from app.db import db

app = create_app('development')
manager = Manager(app)

def make_shell_context():
    return dict(app=app, db=db)

manager.add_command('shell', Shell(make_context=make_shell_context))

migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()


