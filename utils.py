import os.path

import json
from pprint import pprint

from datetime import datetime


def log(*args, **kwargs):
    print("[{}]: ".format(datetime.now()), *args, **kwargs)


def safe_commit(instance):
    from app import db
    try:
        db.session.add(instance)
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        return False


def raw_headers_to_dict(raw_headers):
    """
    :param raw_headers: head and trail no \n
    :return: headers dcit
    """
    a = raw_headers.split('\n')
    b = dict([x.split(": ", 1) for x in a])
    return b


# 判断split是否成功
def split_check(split_list):
    if len(split_list) > 1:
        return True
    else:
        return False