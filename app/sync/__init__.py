# coding=utf-8
"""
同步服务模块

提供 bookmarks 资源组的双向同步功能（pull/push）
"""
from flask import Blueprint

bp = Blueprint('sync', __name__)

from . import views
