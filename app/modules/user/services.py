from marshmallow import fields, Schema, ValidationError

from app.extensions import db
from app.models.circles import Circle, CircleMemberTable, Clockin, CircleMember
from app.models.user import User

from app.modules.errors import MISS_DATA, SUCCESS
from app.modules.schemas import CircleSchema, UserSchema


class UserSchema_v2(Schema):
    UserID = fields.Int(attribute="id")
    avatar = fields.Str(attribute='avatar_url')
    Username = fields.Str(attribute="username")
    nickname = fields.Str(attribute="nickname")
    signature = fields.Str(attribute="signature")

class UserListSvc:

    def get_by_id(self, id):
        schema = UserSchema_v2()
        user = User.query.filter_by(id=id).first()
        return schema.dump(user)



class UserSvc:
    """
    用户圈子相关的接口
    """

    def __init__(self, user_id):
        self.user = User.query.filter_by(id=user_id).first()
        self.user_id = user_id

    def get_join_circles(self): #  Circle.query
        circles = db.session.query(Circle)\
            .join(CircleMember, CircleMember.circle_id==Circle.id)\
            .filter(CircleMember.user_id == self.user_id)\
            .all()
        schema = CircleSchema(many=True)
        result = schema.dump(circles)
        return result

    def get_other_cicles(self): #  Circle.query
        cirlcles_all = db.session.query(Circle).all()
        joined_circles = db.session.query(Circle) \
            .join(CircleMember, CircleMember.circle_id == Circle.id) \
            .filter(CircleMember.user_id == self.user_id) \
            .all()
        other_circles = list(set(cirlcles_all) - set(joined_circles))
        schema = CircleSchema(many=True)
        result = schema.dump(other_circles)
        return result

    def get_user_info(self):
        schema = UserSchema_v2()
        return schema.dump(self.user)



    def update_user_info(self, **update_data):
        user = User.query.filter_by(id=self.user.id).first()
        if user:
            schema = UserSchema()
            result = schema.load(update_data)
            if result.get('nickname'):
                user.nickname = result.get('nickname')
            if result.get('sex_desc'):
                user.sex_desc = result.get('sex_desc')
            if result.get('password'):
                user.password = result.get('password')
            db.save(user)

            ret = schema.dump(user)
            return {"msg": "更新成功", 'code': 1}
        else:
            return {}

    def delete(self, id):
        circle = Circle.query.filter_by(id=id).first()
        if circle:
            db.session.delete(circle)
            return {"msg": "删除成功"}
        else:
            return {"msg": "对象不存在"}



