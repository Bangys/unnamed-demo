import os
import requests
from pyquery import PyQuery as pq

from app.models.board import Board
from app.models.post import Post
from spider import SpiderBook
from utils import safe_commit


def cached_url(url):
    item = SpiderBook.query.filter_by(url=url).first()

    if item is not None:
        return item.base_html
    else:
        item = SpiderBook()
        item.url = url
        headers = {
            'user-agent': '''Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.98 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8''',
        }
        r = requests.get(url, headers)
        item.base_html = r.content
        safe_commit(item)
        return item.base_html


def movie_from_div(div):
    """
    处理一个div的信息
    """
    e = pq(div)
    board_id = Board.query.filter_by(title='books').first()
    form = {
        'title': '{}——评分{}'.format(e('.title').text(), e('.rating_num').text()),
        'content': '豆瓣排名{}, {}'.format(e('.pic').find('em').text(), e('.inq').text()),
        'board_id': board_id.id if board_id is not None else 1,
        'user_id': 1,

    }
    item = Post(form)
    # m.cover_url = e('img').attr('src')
    safe_commit(item)
    return item


def movies_from_url(url):
    page = cached_url(url)
    e = pq(page)
    items = e('.item')
    movies = [movie_from_div(i) for i in items]
    return movies


def download_image(url):
    folder = "img"
    name = url.split("/")[-1]
    path = os.path.join(folder, name)

    if not os.path.exists(folder):
        os.makedirs(folder)

    if os.path.exists(path):
        return

    headers = {
        'user-agent': '''Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.98 Safari/537.36
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8''',
    }
    # 发送网络请求, 把结果写入到文件夹中
    r = requests.get(url, headers)
    with open(path, 'wb') as f:
        f.write(r.content)


def main():
    for i in range(0, 250, 25):
        url = 'https://movie.douban.com/top250?start={}'.format(i)
        try:
            movies_from_url(url)
        except Exception as e:
            print(e)
