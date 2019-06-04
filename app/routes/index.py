from datetime import datetime
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
from utils import log, safe_commit
from app import db

main = Blueprint('index', __name__)


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
        flash('个人页面需要登录后显示', 'warning')
        return redirect(url_for('.index'))
    else:
        return render_template('profile.html', user=u)


@main.route('/search')
def search():
    return render_template('404.html')


@main.route("/profile-up", methods=['POST'])
def profile_change():
    form = request.form
    person = User.query.filter_by(id=form.get('id', -1)).first()
    oldpwd = form.get('old-password', '')
    if person.password != person.salted_password(oldpwd):
        flash('修改失败：原始密码输入错误', 'danger')
        return redirect(url_for('.profile'))
    person.name = form.get('name', '')
    person.email = form.get('email', '')
    person.password = person.salted_password(form.get('password', ''))
    person.ut = datetime.utcnow()

    try:
        db.session.add(person)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash('修改失败：{}'.format(e), 'danger')
        return redirect(url_for('.profile'))

    flash('修改成功', 'success')
    return redirect(url_for('.profile'))
