from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from config import config
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
    """
    在 flask 中，模块化路由的功能由 蓝图（Blueprints）提供
    蓝图可以拥有自己的静态资源路径、模板路径（现在还没涉及）
    用法如下
    """
    # 注册蓝图
    # 有一个 url_prefix 可以用来给蓝图中的每个路由加一个前缀
    from app.routes.index import main as index_routes
    from app.routes.post import main as post_routes
    from app.routes.comment import main as comment_routes
    from app.routes.board import main as board_routes

    app.register_blueprint(index_routes)
    app.register_blueprint(post_routes, url_prefix='/post')
    app.register_blueprint(comment_routes, url_prefmderix='/comment')
    app.register_blueprint(board_routes, url_prefix='/board')

    return app
