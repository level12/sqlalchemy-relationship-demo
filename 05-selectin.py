import sqltap
import sqlalchemy as sa

from utils import Base, MethodsMixin, Session, init_entities, enable_logging


class Blog(Base, MethodsMixin):
    __tablename__ = 'blogs'

    id = sa.Column(sa.Integer, primary_key=True)

    # lazy = True / 'joined' are the same
    comments = sa.orm.relationship(lambda: Comment, lazy='selectin', backref='blog')


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
        # Note that b.comments does not have to be accessed in order for the comments
        # query to be ran.
        assert b.id

query_stats = profiler.collect()
assert len(query_stats) == 2
