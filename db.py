from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Your classes here
user_post_table = db.Table('user_post', db.Model.metadata,
                           db.Column('users_id', db.Integer,
                                     db.ForeignKey('users.id')),
                           db.Column('posts_id', db.Integer,
                                     db.ForeignKey('posts.id'))
                           )


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    upvotes = db.Column(db.Integer, nullable=False)
    body_post = db.Column(db.String, nullable=False)
    users = db.relationship(
        'User', secondary=user_post_table, back_populates='postUser')
    comments = db.relationship('Comment', cascade='delete')

    def __init__(self, **kwargs):
        self.upvotes = kwargs.get('name', '')
        self.body_post = kwargs.get('post', '')
        self.users = []
        self.comments = []

    def serialize(self):
        return {
            'id': self.id,
            'upvotes': self.upvotes,
            'body_post': self.body_post,
            'users': [u.serialize() for u in self.users]
        }


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    posts = db.relationship(
        'Posts', secondary=user_post_table, back_populates='')
