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


class Blog(Base, MethodsMixin):
    __tablename__ = 'blogs'

    id = sa.Column(sa.Integer, primary_key=True)

    # lazy = True / 'joined' are the same
    comments = sa.orm.relationship(lambda: Comment, lazy='subquery_deferred', backref='blog')


class Comment(Base, MethodsMixin):
    __tablename__ = 'comments'

    id = sa.Column(sa.Integer, primary_key=True)
    blog_id = sa.Column(sa.ForeignKey(Blog.id, ondelete='cascade'), nullable=False)


b1 = Blog.add()
b2 = Blog.add()

Comment.add(blog=b1)
Comment.add(blog=b1)
Comment.add(blog=b2)
Comment.add(blog=b2)

sess.commit()

assert sess.query(Blog).count() == 2
assert sess.query(Comment).count() == 4


# Would result in one SQL query.  Because Blog.comments is not accessed, the subquery is never
# issued.
for b in sess.query(Blog):
    assert b.id

# Would result in two SQL Queries.  One issue as soon as the query is ran, to get all blog
# records.
for b in sess.query(Blog):
    # The second query is issued the first time .comments is accessed, to load all comments for
    # all blog records in the parent query.  Therefore, we avoid n+1 queries, but only issue
    # eager queries when collections are actually used.
    assert b.comments
