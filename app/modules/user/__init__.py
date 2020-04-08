# -*- coding:utf-8 -*-
from app.extensions.api import ApiNamespace

from ..api import api
from .resources import UserRsc
from .services import UserSvc


def add_resources(app, **kwargs):
    from . import resources
    ns = ApiNamespace('/users', api)
    ns.add_resource(resources.UserRsc, '/i')
    ns.add_resource(resources.UserListRsc, '/<int:id>')


def init_module(app, **kwargs):
    add_resources(app, **kwargs)
