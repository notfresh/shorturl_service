from app.db import db


class ShortURL(db.Model):
    __tablename__ = 'urls'
    id = db.Column(db.Integer, primary_key=True)

    origin_url = db.Column(db.String(256), index=True)
    shorten_url = db.Column(db.String(32), unique=True) # 务必建立唯一索引
    created_at = db.Column(db.DateTime())  # start_at_desc

    def __repr__(self):
        return "URL origin %s, shorten %s" % self.origin_url[:16], self.shorten_url