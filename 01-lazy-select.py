import sqltap
import sqlalchemy as sa

from utils import Base, MethodsMixin, Session, init_entities, enable_logging


class Blog(Base, MethodsMixin):
    __tablename__ = 'blogs'

    id = sa.Column(sa.Integer, primary_key=True)

    # lazy = False / 'select' is the default.
    comments = sa.orm.relationship(lambda: Comment, lazy='select', backref='blog')


class Comment(Base, MethodsMixin):
    __tablename__ = 'comments'

    id = sa.Column(sa.Integer, primary_key=True)
    blog_id = sa.Column(sa.ForeignKey(Blog.id, ondelete='cascade'), nullable=False)


init_entities(Blog, Comment)
enable_logging()

sess = Session()

profiler = sqltap.ProfilingSession()
with profiler:
    for b in sess.query(Blog):
        assert b.comments

query_stats = profiler.collect()
assert len(query_stats) == 3
