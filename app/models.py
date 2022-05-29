from app.db import db
from werkzeug.security import check_password_hash, generate_password_hash

class ShortURL(db.Model):
    __tablename__ = 'urls'
    id = db.Column(db.Integer, primary_key=True)

    origin_url = db.Column(db.String(256), index=True)
    shorten_url = db.Column(db.String(32), unique=True) # 务必建立唯一索引
    created_at = db.Column(db.DateTime())  # start_at_desc

    def __repr__(self):
        return "URL origin %s, shorten %s" % (self.origin_url[:16], self.shorten_url)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(256), index=True)
    password_hash = db.Column(db.String(256))
    user_type = db.Column(db.Integer) # 用户类型,1表示超级管理员,2表示普通用户

    @property
    def password(self):
        raise AttributeError("No password attr")

    @password.setter
    def password(self, pwd):
        self.password_hash = generate_password_hash(pwd)

    def check_password(self,pwd):
        return check_password_hash(self.password_hash, pwd)


