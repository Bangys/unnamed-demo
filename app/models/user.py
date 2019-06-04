from datetime import datetime
from app import db


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
    username = db.Column(db.String(32))
    email = db.Column(db.String(32))
    password = db.Column(db.String(128))
    ct = db.Column(db.DateTime, default=datetime.utcnow)
    ut = db.Column(db.DateTime)

    def __init__(self, form):
        self.id = form.get('id', None)
        self.name = form.get('name', '')
        self.username = form.get('username', '')
        self.email = form.get('email', '')
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
        if User.query.filter_by(username=name).first() is None:
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
