import hashlib
from datetime import datetime

from flask import current_app

from app.db import db
from werkzeug.security import check_password_hash, generate_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from flask_login import UserMixin, AnonymousUserMixin

class ShortURL(db.Model):
    __tablename__ = 'urls'
    id = db.Column(db.Integer, primary_key=True)
    origin_url = db.Column(db.String(256), index=True)
    shorten_url = db.Column(db.String(32), unique=True) # 务必建立唯一索引
    created_at = db.Column(db.DateTime())  # start_at_desc
    created_by = db.Column(db.Integer)  # owner

    def __repr__(self):
        return "URL origin %s, shorten %s" % (self.origin_url[:16], self.shorten_url)


class User(db.Model,UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(256), index=True)
    password_hash = db.Column(db.String(256))
    user_type = db.Column(db.Integer) # 用户类型,1表示超级管理员,2表示普通用户
    email = db.Column(db.String(64), unique=True, index=True)
    member_since = db.Column(db.DateTime(), default=datetime.now)
    last_seen = db.Column(db.DateTime(), default=datetime.now)
    confirmed = db.Column(db.Boolean, default=True) # TODO some problems with the sendmail lib or config

    def ping(self):
        self.last_seen = datetime.now()
        db.session.add(self)

    @property
    def password(self):
        raise AttributeError("No password attr")

    @password.setter
    def password(self, pwd):
        self.password_hash = generate_password_hash(pwd)

    def check_password(self,pwd):
        return check_password_hash(self.password_hash, pwd)

    ###
    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        db.session.add(self)
        return True
    ###


    def generate_auth_token(self, expiration):
        s = Serializer(current_app.config['SECRET_KEY'],
                       expires_in=expiration)
        return s.dumps({'id': self.id}).decode('ascii')

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])

