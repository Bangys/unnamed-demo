import unittest
from app import create_app, db
from app.models.post import Post
from pyquery import PyQuery as pq


class APITestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_posts(self):
        # 创建文章
        u1 = Post(dict(views=100,
                       title='test post1',
                       content='test post1 content',
                       user_id=1,
                       board_id=1,
                       ))
        u2 = Post(dict(views=100,
                       title='test post2',
                       content='test post2 content',
                       user_id=1,
                       board_id=1,
                       ))

        db.session.add_all([u1, u2])
        db.session.commit()

        # 获取文章
        response = self.client.get(
            '/post/{}'.format(u1.id))
        self.assertEqual(response.status_code, 200)
        html_response = response.get_data(as_text=True)
        e = pq(html_response)
        self.assertEqual(e('#content-md').text(), 'test post1 content')

        response = self.client.get(
            '/post/{}'.format(u2.id))
        self.assertEqual(response.status_code, 200)
        html_response = response.get_data(as_text=True)
        e = pq(html_response)
        self.assertEqual(e('#content-md').text(), 'test post2 content')

    def test_comments(self):
        pass

    def test_boards(self):
        pass

    def test_users(self):
        pass
