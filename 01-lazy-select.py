import sqlalchemy as sa
import sqlalchemy.ext.declarative as sadec
import sqlalchemy.orm as saorm
import sqltap

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


class Blog(Base, MethodsMixin):
    __tablename__ = 'blogs'

    id = sa.Column(sa.Integer, primary_key=True)

    # lazy = False / 'select' is the default.
    comments = sa.orm.relationship(lambda: Comment, lazy='select', backref='blog')


class Comment(Base, MethodsMixin):
    __tablename__ = 'comments'

    id = sa.Column(sa.Integer, primary_key=True)
    blog_id = sa.Column(sa.ForeignKey(Blog.id, ondelete='cascade'), nullable=False)


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

engine.echo = True
sess = Session()

profiler = sqltap.ProfilingSession()
with profiler:
    for b in sess.query(Blog):
        assert b.comments

query_stats = profiler.collect()
assert len(query_stats) == 3

"""
018-06-11 20:36:03,159 INFO sqlalchemy.engine.base.Engine BEGIN (implicit)
2018-06-11 20:36:03,159 INFO sqlalchemy.engine.base.Engine SELECT blogs.id AS blogs_id
FROM blogs
2018-06-11 20:36:03,159 INFO sqlalchemy.engine.base.Engine ()

2018-06-11 20:36:03,161 INFO sqlalchemy.engine.base.Engine SELECT comments.id AS comments_id, comments.blog_id AS comments_blog_id
FROM comments
WHERE ? = comments.blog_id
2018-06-11 20:36:03,161 INFO sqlalchemy.engine.base.Engine (1,)

2018-06-11 20:36:03,162 INFO sqlalchemy.engine.base.Engine SELECT comments.id AS comments_id, comments.blog_id AS comments_blog_id
FROM comments
WHERE ? = comments.blog_id
2018-06-11 20:36:03,162 INFO sqlalchemy.engine.base.Engine (2,)
"""
