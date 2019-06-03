from flask import (
    render_template,
    request,
    redirect,
    session,
    url_for,
    Blueprint,
    flash)
from sqlalchemy import or_, and_

from app.models.board import Board
from app.models.post import Post
from app.models.user import User
from app.routes import current_user
from utils import log

main = Blueprint('index', __name__)

"""
用户登录后, 会写入 session, 并且定向到 /profile
"""


@main.route("/")
def index():
    user = current_user()
    board_name = 'games'
    b = Board.query.filter_by(title=board_name).first()

    if b is None:
        flash('板块验证出错', 'danger')
        return redirect(url_for('post.index'))

    posts = Post.query.filter(and_(Post.image_url != 'noimage',
                                   Post.board_id == b.id)
                              ).order_by(Post.id.desc()).limit(14)
    return render_template("index.html", user=user, posts=posts)


@main.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        form = request.form
        u = User.register(form)
        if u is None:
            flash('用户名已存在', 'danger')
            return render_template("register.html")
        flash('注册成功', 'success')
        session['user_id'] = u.id
        return redirect(url_for('.index'))

    else:
        return render_template("register.html")


@main.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        form = request.form
        u = User.validate_login(form)
        if u is None:
            flash('账号密码错误', 'danger')
            return redirect(url_for('.login'))
        else:
            # session 中写入 user_id
            session['user_id'] = u.id
            # 设置 cookie 有效期
            session.permanent = True
            flash('登录成功', 'success')
            return redirect(url_for('board.index'))
    else:
        return render_template("login.html")


@main.route("/logout", methods=['GET'])
def logout():
    session['user_id'] = ""
    return redirect(url_for('.index'))


@main.route('/profile')
def profile():
    u = current_user()
    if u is None:
        return redirect(url_for('.index'))
    else:
        return render_template('profile.html', user=u)


@main.route('/search')
def search():
    return render_template('404.html')
