from flask import (
    render_template,
    request,
    redirect,
    url_for,
    Blueprint,
    flash)

from app import db
from app.routes import *

from app.models.board import (
    Board,
)
from utils import log

main = Blueprint('board', __name__)


@main.route("/admin")
def index():
    if current_user() is None:
        flash('需要登陆用户操作')
        return redirect(url_for('index.signin'))
    return render_template('board/admin_index.html')


@main.route("/add", methods=["POST"])
def add():
    form = request.form
    u = current_user()
    board = Board(form)
    db.session.add(board)
    db.session.commit()
    return redirect(url_for('topic.index'))
