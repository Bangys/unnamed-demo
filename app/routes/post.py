import time

from flask import (
    render_template,
    request,
    redirect,
    url_for,
    Blueprint,
    flash)

from app import db
from app.routes import *

from app.models.post import Post
from app.models.board import Board
from utils import log

main = Blueprint('post', __name__)

import uuid

csrf_tokens = dict()


@main.route("/")
def index():
    u = current_user()
    board_name = request.args.get('board_name', '')
    if board_name == '':
        posts = Post.query.all()
    else:
        b = Board.query.filter_by(title=board_name).first()
        log('b', b)
        posts = Post.query.filter_by(board_id=b.id).all()
    token = str(uuid.uuid4())
    u = current_user()
    # 防csrf
    if u is not None:
        csrf_tokens['token'] = u.id
    bs = Board.query.all()
    return render_template("post/post_index.html", posts=posts, token=token, bs=bs, board_name=board_name)


@main.route('/<int:id>')
def detail(id):
    u = current_user()
    post = Post.query.filter_by(id=id).first()
    if post is None:
        flash('文章不存在', 'warning')
        return redirect('/')
    post.click()
    board = Board.query.filter_by(id=post.board_id).first()
    author = User.query.filter_by(id=post.user_id).first()
    date = post.ct
    return render_template("post/detail.html", post=post, board=board, author=author, date=date, current_user=u)


@main.route("/add", methods=["POST"])
def add():
    form = request.form
    u = current_user()
    if u is None:
        flash('需要进行登陆', 'info')
        return redirect(url_for('index.login'))
    post = Post(form)
    post.user_id = u.id
    db.session.add(post)
    db.session.commit()
    flash('提交成功', 'success')
    return redirect(url_for('.detail', id=post.id))


@main.route("/delete")
def delete():
    id = int(request.args.get('id'))
    log('args', request.args)
    token = request.args.get('token')
    u = current_user()
    # 判断 token 是否是我们给的
    # if token in csrf_tokens and csrf_tokens[token] == u.id:
    Post.query.filter_by(id=id).delete()
    db.session.commit()
    return redirect(url_for('.index'))

    # else:
    # abort(403)


@main.route("/new")
def new():
    u = current_user()
    if u is None:
        flash('需要进行登陆', 'info')
        return redirect(url_for('index.login'))
    bs = Board.query.all()
    return render_template("post/create.html", bs=bs)
