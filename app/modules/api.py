# -*- coding:utf-8 -*-
from flask import Blueprint


blueprint = Blueprint('noAuth', __name__, url_prefix='/')
# login_required_url
auth_blueprint = Blueprint('auth', __name__, url_prefix='/auth')


def init_module(app, **kwargs):
    app.register_blueprint(blueprint)
    app.register_blueprint(auth_blueprint)


@blueprint.before_request
def before_request():
    pass


