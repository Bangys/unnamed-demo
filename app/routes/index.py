from flask import (
    render_template,
    request,
    redirect,
    session,
    url_for,
    Blueprint,
    flash)

from app.models.user import User
from utils import log

main = Blueprint('index', __name__)


def current_user():
    # 从 session 中找到 user_id 字段, 找不到就 -1
    # 然后 User.find_by 来用 id 找用户
    # 找不到就返回 None
    uid = session.get('user_id', -1)
    u = User.query.filter_by(id=uid).first()
    return u


"""
用户登录后, 会写入 session, 并且定向到 /profile
"""


@main.route("/")
def index():
    user = current_user()
    return render_template("index.html", user=user)


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
