from app.db import db


class TestModel(db.Model):
    __tablename__ = 'test'
    attr1 = db.Column(db.String(32))
    attr2 = db.Column(db.Integer())
    attr3 = db.Column(db.DateTime()) # 必须DT都大写

