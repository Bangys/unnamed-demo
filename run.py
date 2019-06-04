from app import create_app, db

from app.models.board import Board
from app.models.post import Post
from app.models.user import User
from app.models.comment import Comment

from spider import *


def test():
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


# 运行代码
if __name__ == '__main__':
    config = dict(
        debug=True,
        host='127.0.0.1',
        port=5000,
    )
    app = create_app('default')
    app.run(**config)
    # test()
