import os
from random import random
from time import sleep

import requests
from selenium import webdriver
from pyquery import PyQuery as pq

from app.models.board import Board
from app.models.post import Post
from spider import SpiderGame
from utils import safe_commit


# 页面缓存
def cached_url(url):
    item = SpiderGame.query.filter_by(url=url).first()

    if item is not None:
        return item.base_html
    else:
        item = SpiderGame()
        item.url = url
        headers = {
            'user-agent': '''Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36''',
        }
        base_html = requests.get(url, headers).content
        item.base_html = base_html
        safe_commit(item)
        return item.base_html


# 处理单个url
def news_from_url(url):
    site_url = "http://127.0.0.1:5000/"
    base_html = cached_url(url)
    e = pq(base_html)
    p_list = e('article .topicContent p').text()
    title = e('.art_tit').text()
    time = e('.time_box').text()
    content = p_list.replace('。', '。\n')
    # 图片的已知几种情况
    img_url = e('.vg_insert_img img').attr('src')
    if img_url is None:
        img_url = e('.vg_short_img_box img').attr('alt')

    img_path = download_image(img_url)

    if img_path != 'noimage':
        content = '![]({})\n'.format(site_url + img_path) + p_list.replace('。', '。\n')

    board_id = Board.query.filter_by(title='games').first()
    form = {
        'title': title,
        'content': content,
        'board_id': board_id.id if board_id is not None else 1,
        'user_id': 1,
        'ct': time,
        'image_url': img_path,

    }
    item = Post(form)
    safe_commit(item)
    return item


# 处理url列表
def news_from_urllist(url_list):
    for url in url_list:
        sleep(random() * 10)
        news_from_url(url)
        print('第{}个完成'.format(url_list.index(url)))
    return


# 从首页获取数据url列表
def newslist_from_url(url):
    pre_url = 'http://www.vgtime.com'
    browser = webdriver.Chrome()
    browser.get(url)
    e = pq(browser.page_source)
    items = e('.news')[-1]

    times = pq(items[-1])('.time_box').text()
    while times != '1天前':
        sleep(0.5)
        browser.find_element_by_id('topicList_more').click()

        e = pq(browser.page_source)
        items = e('.news')[-1]
        times = pq(items[-1])('.time_box').text()

    e = pq(browser.page_source)
    news = e('.news')
    url_list = [pre_url + pq(i)('.info_box a').attr('href') for i in news]
    news_from_urllist(url_list)

    return url_list


def download_image(url):
    if url is None:
        return 'noimage'
    folder = os.path.join("app", "static", "img")
    name = url.split("/")[-1]
    path = os.path.join(folder, name)

    if not os.path.exists(folder):
        os.makedirs(folder)

    if os.path.exists(path):
        return path.replace(os.sep, '/')[3:]

    headers = {
        'user-agent': '''Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36''',
    }
    r = requests.get(url, headers)
    with open(path, 'wb') as f:
        f.write(r.content)
    return path.replace(os.sep, '/')[3:]


def main():
    url = 'http://www.vgtime.com/topic/index.jhtml'
    try:
        newslist_from_url(url)
    except Exception as e:
        print('games main', e)
