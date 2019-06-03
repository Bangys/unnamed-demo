from app import create_app, db

from app.models.board import Board
from app.models.post import Post
from app.models.user import User
from app.models.comment import Comment

from spider import *


app = create_app('default')

# 运行代码
if __name__ == '__main__':
    # debug 模式可以自动加载你对代码的变动, 所以不用重启程序
    # host 参数指定为 '0.0.0.0' 可以让别的机器访问你的代码
    config = dict(
        debug=True,
        host='127.0.0.1',
        port=5000,
    )

    app.run(**config)
