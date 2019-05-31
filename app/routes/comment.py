from flask import (
    request,
    redirect,
    url_for,
    Blueprint,
    flash)

from app import db
from app.routes import *

from app.models.comment import Comment

main = Blueprint('comment', __name__)


@main.route("/add", methods=["POST"])
def add():
    form = request.form
    u = current_user()
    if u is None:
        flash('需要进行登陆', 'info')
        return redirect(url_for('index.login'))
    comment = Comment(form)
    comment.user_id = u.id
    db.session.add(comment)
    db.session.commit()
    flash('评论成功', 'success')
    return redirect(url_for('post.detail', id=comment.post_id))
