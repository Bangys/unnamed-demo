from datetime import datetime
from config import config
from app.models import Model
from app import db


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32))
    password = db.Column(db.String(128))
    ct = db.Column(db.DateTime, default=datetime.utcnow)
    ut = db.Column(db.DateTime)

    def __init__(self, form):
        self.id = form.get('id', None)
        self.username = form.get('username', '')
        self.password = form.get('password', '')
        self.ct = datetime.utcnow()
        self.ut = self.ct

    def salted_password(self, password, salt='&(*H#OS*DCN#'):  # app.config['SALT']
        import hashlib

        def sha256(ascii_str):
            return hashlib.sha256(ascii_str.encode('ascii')).hexdigest()

        hash1 = sha256(password)
        hash2 = sha256(hash1 + salt)
        return hash2

    @classmethod
    def register(cls, form):
        name = form.get('username', '')
        pwd = form.get('password', '')
        if len(name) > 2 and User.query.filter_by(username=name).first() is None:
            u = User(form)
            u.password = u.salted_password(pwd)
            db.session.add(u)
            db.session.commit()
            return u
        else:
            return None

    @classmethod
    def validate_login(cls, form):
        u = User(form)
        user = User.query.filter_by(username=u.username).first()
        if user is not None and user.password == u.salted_password(u.password):
            return user
        else:
            return None

#
# class User(Model):
#     """
#     User 是一个保存用户数据的 model
#     现在只有两个属性 username 和 password
#     """
#
#     def __init__(self, form):
#         self.id = form.get('id', None)
#         self.username = form.get('username', '')
#         self.password = form.get('password', '')
#
#     def salted_password(self, password, salt='$!@><?>HUI&DWQa`'):
#         import hashlib
#         def sha256(ascii_str):
#             return hashlib.sha256(ascii_str.encode('ascii')).hexdigest()
#
#         hash1 = sha256(password)
#         hash2 = sha256(hash1 + salt)
#         return hash2
#
#     def hashed_password(self, pwd):
#         import hashlib
#         # 用 ascii 编码转换成 bytes 对象
#         p = pwd.encode('ascii')
#         s = hashlib.sha256(p)
#         # 返回摘要字符串
#         return s.hexdigest()
#
#     @classmethod
#     def register(cls, form):
#         name = form.get('username', '')
#         pwd = form.get('password', '')
#         if len(name) > 2 and User.find_by(username=name) is None:
#             u = User.new(form)
#             u.password = u.salted_password(pwd)
#             u.save()
#             return u
#         else:
#             return None
#
#     @classmethod
#     def validate_login(cls, form):
#         u = User(form)
#         user = User.find_by(username=u.username)
#         if user is not None and user.password == u.salted_password(u.password):
#             return user
#         else:
#             return None
