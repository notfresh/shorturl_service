from werkzeug.security import generate_password_hash, check_password_hash
from app.db import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'user'
    username = db.Column(db.String(32), unique=True)  # 登录用户名，不可修改，不做显示
    password_hash = db.Column(db.String(256))
    phone = db.Column(db.String(11), unique=True)
    email = db.Column(db.String(64), unique=True)
    sex = db.Column(db.SmallInteger, default=0) # 性别
    nickname = db.Column(db.String(64)) # 页面显示的用户名
    avatar_url = db.Column(db.String(2048))
    user_wechat_id = db.Column(db.Integer)
    wechat_account = db.Column(db.String(64)) # 微信账号
    sex_desc = db.Column(db.String(8), default="未知")  # 性别

    @property
    def password(self):
        return ''

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User %r>' % (self.username if self.username else self.id)

