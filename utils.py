import os.path
import time
import json


def log(*args, **kwargs):
    # time.time() 返回 unix time
    format = '%H:%M:%S'
    value = time.localtime(int(time.time()))
    dt = time.strftime(format, value)
    print(dt, *args, **kwargs)


def safe_commit(instance):
    from app import db
    try:
        db.session.add(instance)
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        return False
