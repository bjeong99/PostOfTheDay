from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

# Your classes here


class Post(db.Model):
    __tablename__ = 'posts_table'
    id = db.Column(db.Integer, primary_key=True)
    upvotes = db.Column(db.Integer, nullable=False)
    body_post = db.Column(db.String, nullable=False)
    time_stamp = db.Column(db.DateTime, nullable=False)
    date = db.Column(db.Date, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'users_table.id'), nullable=False)
    comments = db.relationship('Comment', cascade='delete')

    def __init__(self, **kwargs):
        self.upvotes = kwargs.get('upvotes', '')
        self.body_post = kwargs.get('body_post', '')
        self.time_stamp = kwargs.get('time_stamp', '')
        self.date = kwargs.get('date', '')
        self.user_id = kwargs.get('user_id', '')

    def serialize(self):
        return {
            'id': self.id,
            'upvotes': self.upvotes,
            'body_post': self.body_post,
            'user_id': self.user_id,
            'time_stamp': format(self.time_stamp),
            'comments': [c.serialize() for c in self.comments]
        }


class User(db.Model):
    __tablename__ = 'users_table'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    posts = db.relationship('Post', cascade='delete')
    comments = db.relationship('Comment', cascade='delete')

    def __init__(self, **kwargs):
        self.username = kwargs.get('username', '')
        self.posts = []

    def serialize(self):
        return{
            'id': self.id,
            'username': self.username,
            'posts': [p.serialize() for p in self.posts],
            'comments': [c.serialize() for c in self.comments]
        }


class Comment(db.Model):
    __tablename__ = 'comments_table'
    id = db.Column(db.Integer, primary_key=True)
    body_comment = db.Column(db.String, nullable=False)
    time_stamp = db.Column(db.DateTime, nullable=False)
    date = db.Column(db.Date, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'users_table.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey(
        'posts_table.id'), nullable=False)

    def __init__(self, **kwargs):
        self.body_comment = kwargs.get('body_comment', '')
        self.time_stamp = kwargs.get('time_stamp', '')
        self.date = kwargs.get('date', '')
        self.user_id = kwargs.get('user_id', '')
        self.post_id = kwargs.get('post_id', '')

    def serialize(self):
        return{
            'id': self.id,
            'body_comment': self.body_comment,
            'time_stamp': format(self.time_stamp),
            'user_id': self.user_id,
            'post_id': self.post_id
        }
