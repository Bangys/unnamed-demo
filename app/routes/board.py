from flask import (
    render_template,
    request,
    redirect,
    url_for,
    Blueprint,
    flash)

from app import db

from app.models.board import (
    Board,
)
from app.routes import current_user
from utils import log

main = Blueprint('board', __name__)


@main.route("/admin")
def index():
    user = current_user()
    if user is None:
        flash('需要登陆用户操作', 'warning')
        return redirect(url_for('index.login'))
    bs_all = Board.query.all()
    return render_template('board/admin_index.html', bs_all=bs_all, user=user)


@main.route("/add", methods=["POST"])
def add():
    form = request.form
    log('add', form)
    u = current_user()
    name = form.get('name', '')
    title = form.get('title', '')
    if Board.query.filter_by(name=name).first() is not None:
        flash("该板块名已存在", 'danger')
        return redirect(url_for('.index'))
    if Board.query.filter_by(title=title).first() is not None:
        flash("该tag已存在", 'danger')
        return redirect(url_for('.index'))
    board = Board(form)
    db.session.add(board)
    db.session.commit()
    flash('添加板块成功', 'success')
    return redirect(url_for('.index'))
