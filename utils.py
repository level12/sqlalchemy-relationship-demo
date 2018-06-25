import logging
import sys

import sqlalchemy as sa
import sqlalchemy.ext.declarative as sadec
import sqlalchemy.orm as saorm

engine = sa.create_engine('sqlite:///')

meta = sa.MetaData()
Base = sadec.declarative_base(metadata=meta)

Session = saorm.sessionmaker(bind=engine)
sess = Session()

class MethodsMixin:
    @classmethod
    def add(cls, **kwargs):
        obj = cls(**kwargs)
        sess.add(obj)
        return obj


def enable_logging():
    line = '-' * 100
    formatter = logging.Formatter(f'%(message)s\n{line}')
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    handler.setLevel(logging.INFO)
    sa_eng_logger = logging.getLogger('sqlalchemy.engine')
    sa_eng_logger.setLevel(logging.INFO)
    sa_eng_logger.addHandler(handler)


def init_entities(Blog, Comment):
    meta.create_all(bind=engine)

    b1 = Blog.add()
    b2 = Blog.add()

    Comment.add(blog=b1)
    Comment.add(blog=b1)
    Comment.add(blog=b2)
    Comment.add(blog=b2)

    sess.commit()

    assert sess.query(Blog).count() == 2
    assert sess.query(Comment).count() == 4
