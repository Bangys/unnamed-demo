from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from config import config
from config import Config as CF
from utils import log

bootstrap = Bootstrap()
db = SQLAlchemy()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    bootstrap.init_app(app)
    db.init_app(app)

    with app.app_context():
        db.create_all()

        from app.models.board import Board
        from app.models.user import User
        bs = Board.query.all()
        if bs == []:
            init_boards = [{'title': 'news', 'name': '新闻'},
                           {'title': 'games', 'name': '游戏'},
                           {'title': 'books', 'name': '好书'},
                           {'title': 'bala', 'name': '闲聊'}]

            init_user = dict(username=CF.FLASKY_ADMIN, email='admin@example.com',
                             password=CF.FLASKY_PWD)
            db.session.add(User(init_user))

            for b in init_boards:
                db.session.add(Board(b))
            try:
                db.session.commit()
            except Exception as e:
                print('init_board err:', e)

    # url_prefix 路由前缀
    from app.routes.index import main as index_routes
    from app.routes.post import main as post_routes
    from app.routes.comment import main as comment_routes
    from app.routes.board import main as board_routes

    app.register_blueprint(index_routes)
    app.register_blueprint(post_routes, url_prefix='/post')
    app.register_blueprint(comment_routes, url_prefmderix='/comment')
    app.register_blueprint(board_routes, url_prefix='/board')

    return app
