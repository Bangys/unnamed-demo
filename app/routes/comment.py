from flask import (
    request,
    redirect,
    url_for,
    Blueprint,
)

from app import db
from app.routes import *

from app.models.comment import Comment


main = Blueprint('comment', __name__)


@main.route("/add", methods=["POST"])
def add():
    form = request.form
    u = current_user()
    comment = Comment(form)
    comment.user_id = u.id
    db.session.add(comment)
    db.session.commit()

    return redirect(url_for('post.detail', id=comment.post_id))

