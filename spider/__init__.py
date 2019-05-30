from app import db
from datetime import datetime
from sqlalchemy.dialects.mysql import LONGTEXT


class SpiderBook(db.Model):
    __tablename__ = 'spider_book'
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(64))
    base_html = db.Column(LONGTEXT)
    ct = db.Column(db.DateTime, default=datetime.utcnow)
    ut = db.Column(db.DateTime, default=ct)

    def __repr__(self):
        name = self.__class__.__name__
        properties = ('{}=({})'.format(k, v) for k, v in self.__dict__.items())
        s = '\n<{} \n  {}>'.format(name, '\n  '.join(properties))
        return s
