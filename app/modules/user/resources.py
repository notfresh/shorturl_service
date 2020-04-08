# -*- coding:utf-8 -*-
import os
from flask import request

from app.utils import CommonResource
from app.extensions import cos
from app.modules.errors import MISS_DATA, SUCCESS

from .services import UserSvc, UserListSvc
from ..jwt import jwt

UPLOAD_FOLDER = 'img_tmp'

class UserRsc(CommonResource):
    def get(self, id):
        """
        获取单个圈子的数据
        :param id:
        :return:
        """
        return UserSvc(id).get_user_info()

    def put(self):
        """
        修改圈子的数据
        :param id: 当前用户的id
        :return:
        """
        data = request.get_json() or {}
        return UserSvc(jwt.visitor.id).update_user_info(**data)


class UserListRsc(CommonResource):
    def get(self, id):
        """
        获取单个圈子的数据
        :param id:
        :return:
        """
        return UserListSvc().get_by_id(id)






