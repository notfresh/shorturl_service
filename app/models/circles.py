from app.db import db


class Circle(db.Model):
    __tablename__ = 'circles'
    name = db.Column(db.String(32))
    type = db.Column(db.String(8))
    # start_at_desc = db.Column(db.DateTime()) # start_at_desc
    # end_at_desc = db.Column(db.DateTime()) # end_at

    start_at = db.Column(db.String(32))
    end_at = db.Column(db.String(32))

    desc = db.Column(db.String(128))
    check_rule = db.Column(db.String(256))
    circle_master_id = db.Column(db.Integer())
    avatar = db.Column(db.String(256)) # 头像地址
    joined_number = db.Column(db.Integer()) # 加入人数
    is_published = db.Column(db.Integer()) # 草稿状态为0，没有发布，发布状态为1， 已经发布

    def update_joined_number(self):
        self.joined_number += 1


class CircleMemberTable(db.Model):
    __tablename__ = 'circles_members'
    circle_id = db.Column(db.Integer(), index=True)  # 圈子id
    user_id = db.Column(db.Integer(), index=True)  # 用户ID

    @classmethod
    def add(cls, circle, user):
        obj = cls()
        obj.user_id = user.id
        obj.circle_id = circle.id
        db.save(obj)
        return obj

    @classmethod
    def delete(cls, circle, user):
        # db.session.delete(circle)
        item = cls.query.filter(cls.circle_id == circle.id).filter(cls.user_id == user.id).first()
        if item:
            db.session.delete(item)
            db.session.commit()
        return circle


class Clockin(db.Model):
    __tablename__ = 'clockin'
    circle_id = db.Column(db.Integer(), index=True)  # 圈子id
    user_id = db.Column(db.Integer(), index=True)  # 用户ID
    line = db.Column(db.String(256)) # 打卡配的台词
    clockin_img = db.Column(db.String(256)) # 打卡地址


CircleMember = CircleMemberTable

