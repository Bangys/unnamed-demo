import time
from datetime import datetime

from app import db

from app.models import Model
# class Board(Model):
#     def __init__(self, form):
#         self.id = None
#         self.title = form.get('title', '')
#         self.name = form.get('name', '')
#         self.ct = int(time.time())
#         self.ut = self.ct




class Board(db.Model):
    __tablename__ = 'board'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64))
    name = db.Column(db.String(64), unique=True)
    ct = db.Column(db.DateTime, default=datetime.utcnow)
    ut = db.Column(db.DateTime, default=ct)

    def __init__(self, form):
        self.title = form.get('title', '')
        self.name = form.get('name', '')
        self.ct = datetime.utcnow()
        self.ut = self.ct
