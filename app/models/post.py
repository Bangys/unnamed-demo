from datetime import datetime
from app import db
from utils import log


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
        self.title = form.get('title', '')
        self.content = form.get('content', '')
        self.board_id = form.get('board_id', 1)
        self.ct = datetime.utcnow()
        self.ut = self.ct

    def click(self):
        self.views += 1
        try:
            db.session.commit()
        except Exception as e:
            log(e)
        return

    def comments(self):
        from .comment import Comment
        comments = Comment.query.filter_by(post_id=self.id).all()
        return comments
