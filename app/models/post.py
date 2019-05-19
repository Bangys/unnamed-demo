import time
from datetime import datetime
from app import db
from app.models import Model
from utils import log

#
# class Topic(Model):
#     @classmethod
#     def get(cls, id):
#         m = cls.find_by(id=id)
#         m.views += 1
#         m.save()
#         return m
#
#     def __init__(self, form):
#         self.id = None
#         self.views = 0
#         self.title = form.get('title', '')
#         self.content = form.get('content', '')
#         self.ct = int(time.time())
#         self.ut = self.ct
#         self.user_id = form.get('user_id', '')
#         self.board_id = int(form.get('board_id', -1))
#
#     def replies(self):
#         from .reply import Reply
#         ms = Reply.find_all(topic_id=self.id)
#         return ms
#
#     def board(self):
#         from .board import Board
#         m = Board.find(self.board_id)
#         return m


class Post(db.Model):
    __tablename__ = 'post'

    id = db.Column(db.Integer, primary_key=True)
    views = db.Column(db.Integer, default=0)
    title = db.Column(db.String(64))
    content = db.Column(db.Text)
    ct = db.Column(db.DateTime, default=datetime.utcnow)
    ut = db.Column(db.DateTime)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    board_id = db.Column(db.Integer, db.ForeignKey('board.id', ondelete='CASCADE'))

    def __init__(self, form):
        self.title = form.get('title')
        self.content = form.get('content')
        self.ct = datetime.utcnow()
        self.ut = self.ct

    def click(self):
        self.views += 1
        try:
            db.session.commit()
        except Exception as e:
            log(e)
        return

    def replies(self):
        from .comment import Comment
        comments = Comment.query.filter_by(post_id=self.id).all()
        return comments
