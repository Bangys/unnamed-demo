import time

from datetime import datetime

from app import db
from app.models import Model


class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id', ondelete='CASCADE'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    ct = db.Column(db.DateTime, default=datetime.utcnow)
    ut = db.Column(db.DateTime, default=ct)

    def __init__(self, form):
        self.content = form.get('content')
        self.post_id = form.get('post_id')