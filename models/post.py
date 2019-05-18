from app import db
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    Index,
    Text,
)
from datetime import datetime


class Post(db.model):
    id = Column(Integer, primary_key=True)
    content = Column(Text)
    user = Column(String)
    ct = Column(DateTime, default=datetime.now())
    ut = Column(DateTime, default=ct)


