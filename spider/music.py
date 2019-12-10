import os
from random import random
from time import sleep

import redis
from snownlp import SnowNLP
from pyecharts.charts import Bar, Pie, Line
from pyecharts import options as opts
import jieba
from collections import Counter
from pyquery import PyQuery as pq
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from utils import log, split_check


def get_albums(singer_id):
    """
    get singer's all album id
    :param singer_id: 歌手id
    :return: 专辑id列表
    """
    # 通过歌手id获得专辑列表页数
    singer_url = url_prefix + "artist/album?id={}".format(singer_id)
    singer_html = process_url(singer_url)
    singer_content = pq(singer_html)
    album_page_count = singer_content(".u-page a:nth-last-child(2)").text()
    if album_page_count == '':
        album_page_count = 0
    elif album_page_count is not None:
        album_page_count = int(album_page_count)
    else:
        log("获取页数时发生错误")
        exit()
    # 通过页数计算专辑总数并获取
    albums_url = singer_url + "&limit={}&offset=0".format((album_page_count + 1) * 12)
    album_html = process_url(albums_url)
    album_content = pq(album_html)
    albums_ids = [album.attrib['data-res-id'] for album in album_content("#m-song-module li div a:nth-child(3)")]
    return albums_ids


def process_lyric_from_html(song_content):
    try:
        data = song_content("#lyric-content").text()[:-3] + song_content("#flag_more").text()
    except Exception as e:
        log("歌词获取异常：{}".format(song_content(".cnt p:nth-child(2) a").attr("href").split("=")[1]))
        data = "无歌词"
    return data


def process_song(song_id):
    """
    歌曲id、歌曲名、歌手id、所属专辑id、歌词、评论数
    process song information
    :param song_id: 歌曲id
    :return: 处理状态(True or False)
    """
    log("正在处理歌曲：{}".format(song_id))
    if db.hexists("song:" + song_id, "id"):
        log("有缓存(已做过处理)，歌曲id:{}".format(song_id))
        return True
    else:
        song_url = url_prefix + "song?id={}".format(song_id)
        song_html = process_url(song_url)
        song_content = pq(song_html)
        head_data = song_content(".cnt")
        song_name = head_data(".tit").text()
        # todo 增加多歌手的元素选取
        sid = head_data("p:nth-child(2) a").attr("href").split("=")[1]
        album_id = head_data("p:nth-child(3) a").attr("href").split("=")[1]
        lyric = process_lyric_from_html(song_content)
        comment_count = head_data("#cnt_comment_count").text()
        data = {
            "id": song_id,
            "name": song_name,
            "singer_id": sid,
            "album_id": album_id,
            "lyric": lyric,
            "comment_count": comment_count
        }
        try:
            db.hmset("song:" + song_id, data)
        except Exception as e:
            log("song存入Redis时发生错误:{}".format(e))
            return False
        log("歌曲{}({})处理完毕".format(song_id, song_name))
        return True


def process_album_from_albums(albums_ids):
    """
    process album information
    :param albums_ids: 专辑id列表
    :return: 专辑内所有歌曲id
    """
    count = 0
    result = []
    for album_id in albums_ids:
        count += 1
        log("正在处理第{}个专辑({})".format(count, album_id))
        if db.hexists("album:" + album_id, "id"):
            log("有缓存，专辑id:{}".format(album_id))
            continue
        else:
            album_url = url_prefix + "album?id={}".format(album_id)
            album_html = process_url(album_url)
            album_content = pq(album_html)
            head_data = album_content(".topblk")

            # 专辑信息提取
            sid = head_data("a").attr("href").split("=")[1]
            singer_name = head_data("p:nth-child(2)").text().split("：")[1]
            aid = album_id
            name = head_data("div h2").text()
            image_url = album_content(".j-img").attr("src").split("?")[0]
            company = head_data("p:nth-child(4)").text().split("：")[1] if split_check(
                head_data("p:nth-child(4)").text().split("：")) else ""
            date = head_data("p:nth-child(3)").text().split("：")[1]
            data = {
                "singer_id": sid,
                "singer_name": singer_name,
                "id": aid,
                "name": name,
                "image_url": image_url,
                "company": company.strip(),
                "date": date
            }
            try:
                db.hmset("album:" + album_id, data)
            except Exception as e:
                log("album存入Redis时发生错误:{}".format(e))

            songs_from_album = [song.attrib["href"].split("=")[1] for song in
                                album_content(".m-table tbody tr td:nth-child(2) span a")]
            log("第{}个专辑 {} 处理完毕, 包含{}首歌曲".format(count, name, len(songs_from_album)))

            # 进入歌曲处理
            result.extend([(process_song(sid), sid) for sid in songs_from_album])  # (处理状态, 歌曲id)
    return result


def process_url(url):
    """
    :param url: base url
    :param mode: 0:default
                 1:process song
    :return:
    """
    log("开始处理url:", url)
    # 缓存检查
    html = db.get('page:' + url)
    if html is not None:
        return html
    else:
        headers = """
        accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3
        accept-encoding: gzip, deflate, br
        accept-language: zh-CN,zh;q=0.9,en;q=0.8
        cookie: _ntes_nnid=5ac369ebd35e454bb236f3b83a290c08,1560440292739; s_n_f_l_n3=5cd33d62bfbf413c1560440292751; _ntes_nuid=5ac369ebd35e454bb236f3b83a290c08; UM_distinctid=16bac970e1f2a8-0253f77f185814-e343166-1fa400-16bac970e209d8; vjuids=296bd1d09.16bac975195.0.b890e8f1fed82; mail_psc_fingerprint=a3b4e0297b214cc75cbd182d71e2e14a; WM_TID=BRMJxl3sMwxFQVEBRAMtnmLZZj4DUqWi; _antanalysis_s_id=1567442148247; vjlast=1561968726.1569234271.23; _iuqxldmzr_=32; ne_analysis_trace_id=1572443780375; vinfo_n_f_l_n3=5cd33d62bfbf413c.1.0.1560440292751.0.1572443783859; __f_=1574676268292; playerid=85879344; WM_NI=eRzzZlIUfiN37uIPKrKHHxj%2BaYhSWickK7hjnwZ0Wo8qkZRTHk3UvP9sf7qCxG%2FAjFjplSCS6Vco43d7ZzgSGkiIM5DoXBh%2BC1hsc7dD4DBRvOu8KNrjOgGxZBpVGvDIQ0g%3D; WM_NIKE=9ca17ae2e6ffcda170e2e6eeafae4683f196b9f26ae9b48eb2c55f829a9f85bc3d9aada88bcf3bbaaaad9aee2af0fea7c3b92aa78eb69bd9688b8baa8acd39f5ab87b1ca7a89988899e921a387a8b4d663a1b585d8eb62aea996d1d665fcafa5bbd1608cb5fdb6f55cfbadaad8f449bc99e1a2e94eaab0a4b4c259f68aad90b739a8e9969be65985b5a7aad03f88b198a3eb2181efa894e23da89cfca5c15ab691bbd9ca46b2b68188c6749a9ec0b7c67e88979fd1e637e2a3; JSESSIONID-WYYY=W149o79yogttv%5Cg1B2EmJE6EwmlI2dHEJZz7zsse3o2rmCMEJJKWnVgJFrMdCTiuSiRO9CQyaxgZysSGpshhuZiQEasBljcc5INYEXaecY%2BZZ3bUp6g9eIIiJ7IEuZ%5CHQjG3%2BzP8xYI9QDvWCdiVc8u7X6eMT%2FaCCTVDDR6O%5ChR%5CH9I3%3A1575013385773
        referer: https://music.163.com/
        sec-fetch-mode: nested-navigate
        sec-fetch-site: same-origin
        upgrade-insecure-requests: 1
        user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36
        """
        # phantomJs设置headers
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument(headers)
        browser = webdriver.Chrome(options=chrome_options)
        try:
            browser.get(url)
            browser.switch_to.frame("g_iframe")
            if "album" in url and "artist" not in url:
                WebDriverWait(browser, 60, 1).until(
                    expected_conditions.presence_of_element_located((By.CLASS_NAME, 'cnt')))
            if "song" in url:
                WebDriverWait(browser, 60, 1).until(
                    expected_conditions.presence_of_element_located((By.ID, 'lyric-content')))
                WebDriverWait(browser, 60, 1).until(
                    expected_conditions.presence_of_element_located((By.ID, 'cnt_comment_count')))

            html = browser.page_source
            db.set('page:' + url, html)
            log("已做缓存处理:{}".format(url))
            sleep(random() * 3)

            return html
        except Exception as e:
            log("请求过程出错: {}".format(e))
            db.delete(*db.keys(pattern='album:*'))
            sleep(5)
            main()
            # exit()
        finally:
            browser.close()


def process_emotion(text):
    """
    :param text: lyric text
    :return: score
    """
    lyric_list = text.split("\n")
    while lyric_list[-1] == "":
        lyric_list.pop()
    score = sum([SnowNLP(line).sentiments for line in lyric_list]) / len(lyric_list)
    return score


def process_frequency(text):
    """
    :param text: lyric text
    :return: Counter
    """
    word_list = jieba.cut(text)
    c = Counter()
    for word in word_list:
        if len(word) > 1 and word != '\n':
            c[word] += 1
    return c


def maker_analysis(text):
    """
    :param text: maker info
    :return:
    """


def merge_lyric_text(song):
    """
    :param song: redis key name, ex: b'song:5432'
    :return: (lyric text, maker info)
    """
    lyric = db.hget(song, "lyric").decode("utf-8")
    lyric_list = lyric.split("\n")
    text = ""
    info = ""
    for line in lyric_list:
        if line == "":
            continue
        if ":" in line or "：" in line:
            info += line + "\n"
        else:
            text += line + "\n"
    return text, info


def process_prepare_data(singer_id):
    # 找出歌手所有歌曲
    all_songs = db.scan(0, match="song:*", count=10000)
    target_songs = []
    total_score = 0
    emotion_list = []
    words_count = Counter()
    maker_count = Counter()
    for song in all_songs[1]:
        sid = db.hget(song, "singer_id")
        if sid.decode("utf-8") == str(singer_id):
            target_songs.append(song)

    # 取得所有歌曲并排序
    sorted_songs = [(song, int(db.hget(song, "comment_count").decode("utf-8"))) for song in target_songs]
    sorted_songs.sort(key=lambda x: x[1], reverse=True)
    # log("最热度的前20首歌曲为：{}".format(
    #     [db.hget(song[0], "name").decode("utf-8").replace("\n", "") for song in sorted_songs[:20]]))
    # log("最冷门的前20首歌曲为：{}".format(
    #     [db.hget(song[0], "name").decode("utf-8").replace("\n", "") for song in sorted_songs[-20:]]))

    for song in sorted_songs:
        # 歌词处理 song: (song_id, comment_count)
        text, maker_info = merge_lyric_text(song[0])
        # 歌词的情绪分析
        song_name = db.hget(song[0], "name").decode("utf-8")
        song_score = db.get(b'score:' + song[0])
        if song_score is None:
            song_score = process_emotion(text)
            db.set(b'score:' + song[0], song_score)
            log("歌曲 {} 未发现情绪分，已计算后存入Redis".format(song_name.replace("\n", "")))
        total_score += float(song_score)
        emotion_list.append((song_name, float(song_score)))
        # log("正在处理第{}首歌曲，{}的情绪分为{:.2f}".format(sorted_songs.index(song) + 1, song_name.replace("\n", ""),
        #                                       float(song_score)))

        for line in maker_info.split("\n"):
            if "作词" in line:
                line = SnowNLP(line).han
                if "：" in line:
                    maker_count[line.split("：")[1].strip()] += 1
                else:
                    maker_count[line.split(":")[1].strip()] += 1
        # 词频统计
        words_count.update(process_frequency(text))
        maker_analysis(maker_info)

    # ----图表部分----

    # 歌词情绪分析
    emotion_bar = Bar()
    emotion_x_data = []
    emotion_y_data = []
    for item in sorted(emotion_list, key=lambda x: x[1], reverse=True)[:20]:
        emotion_x_data.append(item[0])
        emotion_y_data.append(round(item[1], 3))

    emotion_bar.add_xaxis(emotion_x_data)
    emotion_bar.add_yaxis("情绪分值", emotion_y_data)
    emotion_bar.set_global_opts(title_opts=opts.TitleOpts(title="歌词情绪好的前20首歌曲"))
    emotion_bar.render("[歌手id-{}]歌词情绪好的前20首歌曲.html".format(singer_id))

    # 作词人统计
    maker_pie = Pie()
    maker_data = []
    for name, times in maker_count.most_common(10):
        maker_data.append((name, times))
    maker_pie.add("出现次数", maker_data)
    maker_pie.set_global_opts(title_opts=opts.TitleOpts(title="合作次数最多的作词人前十名", pos_top="8%"),
                              legend_opts=opts.LegendOpts(pos_left="15%")
                              )
    maker_pie.set_series_opts(label_opts=opts.LabelOpts(formatter="{d}%"))
    maker_pie.render("[歌手id-{}]合作次数最多的作词人前十名.html".format(singer_id))

    # 歌词高频词语
    words_bar = Bar()
    word_x_data = []
    word_y_data = []
    for word, count in words_count.most_common(20):
        word_x_data.append(word)
        word_y_data.append(count)

    words_bar.add_xaxis(word_x_data)
    words_bar.add_yaxis("出现次数", word_y_data, category_gap="25%")
    words_bar.set_global_opts(title_opts=opts.TitleOpts(title="歌词中高频出现的前20个词"))
    words_bar.render("[歌手id-{}]歌词中重复出现的前20个词.html".format(singer_id))

    # 评论热门歌曲TOP30
    hot_line = Line()
    x_data = []
    y_data = []
    for song in sorted_songs[:20]:
        x_data.append(db.hget(song[0], "name"))
        y_data.append(song[1])
    hot_line.add_xaxis(x_data)
    hot_line.add_yaxis("评论数", y_data)
    hot_line.set_global_opts(title_opts=opts.TitleOpts(title="评论最火热的前20首歌曲"))
    hot_line.render("[歌手id-{}]热门歌曲TOP20.html".format(singer_id))

    # 评论冷门歌曲TOP30
    # cool_line = Line()
    # x_data = []
    # y_data = []
    # for song in sorted_songs[-20:]:
    #     x_data.append(db.hget(song[0], "name"))
    #     y_data.append(song[1])
    # cool_line.add_xaxis(x_data)
    # cool_line.add_yaxis("评论数", y_data)
    # cool_line.set_global_opts(title_opts=opts.TitleOpts(title="评论冷清歌曲前20首"))
    # cool_line.render("[歌手id-{}]冷门歌曲TOP20.html".format(singer_id))
    return


def main():
    albums_ids = get_albums(singer_id)
    result = process_album_from_albums(albums_ids)
    res_success = len([x for x in result if x[0] is True])
    log("共处理{}首歌曲，其中成功{}首，失败{}首".format(len(result), res_success, len(result) - res_success))


def redis_check_none(string):
    db = redis.Redis()
    all_song = db.scan(0, match=string, count=10000)
    none_list = []
    for song in all_song[1]:
        item = db.hget(song, "lyric").decode('utf-8')
        if item == "":
            log("none lyric found:", song)
            none_list.append(song.decode("utf-8"))
            db.delete(song)
            db.delete("page:https://music.163.com/song?id=".encode("utf-8") + song.split(b":")[1])
        comment_c = db.hget(song, "comment_count")
        try:
            int(comment_c.decode('utf-8'))
        except Exception as e:
            log("none comment found:", song)
            none_list.append(song.decode("utf-8"))
            db.delete(song)
            db.delete("page:https://music.163.com/song?id=".encode("utf-8") + song.split(b":")[1])
            # 重置

    result = [process_song(x.split(":")[1]) for x in none_list]
    log("check ok, found {}, result: sucess:{}".format(len(none_list), len([x for x in result if x is True])))


def check():
    string = "song:*"
    redis_check_none(string)


if __name__ == "__main__":
    redis_host = "127.0.0.1"
    url_prefix = "https://music.163.com/"
    conn_pool = redis.ConnectionPool(host=redis_host, port=6379)
    db = redis.Redis(connection_pool=conn_pool)
    singer_id = 2116  # 6452 3684 2116 2747
    # main()
    # check()
    process_prepare_data(singer_id)
