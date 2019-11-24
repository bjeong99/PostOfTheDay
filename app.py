import json
from flask import Flask, request
from db import db, Post, User, Comment
import datetime
from sqlalchemy import desc
app = Flask(__name__)
db_filename = 'potd.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///%s' % db_filename
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

db.init_app(app)
with app.app_context():
    db.create_all()


@app.route('/')
# GET all posts (time order)
@app.route('/api/posts/', methods=['GET'])
def get_all_posts():
    posts = Post.query.all()
    res = {'success': True, 'data': [p.serialize() for p in posts]}
    return json.dumps(res), 200

# GET all posts (upvote order)
@app.route('/api/posts/upvote/', methods=['GET'])
def get_all_posts_order():
    posts = Post.query.order_by(desc(Post.upvotes)).all()
    res = {'success': True, 'data': [p.serialize() for p in posts]}
    return json.dumps(res), 200

# POST(create) a post
@app.route('/api/posts/', methods=['POST'])
def make_a_post():
    post_body = json.loads(request.data)
    body_post = post_body.get('body')
    username = post_body.get('username')
    user = User.query.filter_by(username=username).first()
    user_id = user.id
    newPost = Post(
        upvotes=0,
        body_post=body_post,
        time_stamp=format(datetime.datetime.now()),
        user_id=user_id
    )
    db.session.add(newPost)
    db.session.commit()
    return json.dumps({'success': True, 'data': newPost.serialize()}), 201

# GET a specific post
@app.route('/api/post/<int:post_id>/', methods=['GET'])
def get_a_post(post_id):
    post = Post.query.filter_by(id=post_id).first()
    if not post:
        return json.dumps({'success': False, 'error': 'Post not found'}), 404
    return json.dumps({'success': True, 'data': post.serialize()}), 200

# GET top post
@app.route('/api/post/top/', methods=['GET'])
def get_top_post():
    post = Post.query.order_by(desc(Post.upvotes)).first()
    res = {'success': True, 'data': post.serialize()}
    return json.dumps(res), 200

# DELETE a specific post
@app.route('/api/post/<int:post_id>/', methods=['DELETE'])
def delete_a_post(post_id):
    post = Post.query.filter_by(id=post_id).first()
    if not post:
        return json.dumps({'success': False, 'error': 'Post not found'}), 404
    db.session.delete(post)
    db.session.commit()
    return json.dumps({'success': True, 'data': post.serialize()}), 200

# Upvote a post
@app.route('/api/post/<int:post_id>/upvote/', methods=['POST'])
def upvote_post(post_id):
    post = Post.query.filter_by(id=post_id).first()
    if not post:
        return json.dumps({'success': False, 'error': 'Post not found'}), 404
    post.upvotes += 1
    db.session.commit()
    return json.dumps({'success': True, 'data': post.serialize()}), 200

# GET users
@app.route('/api/users/', methods=['GET'])
def get_users():
    users = User.query.all()
    res = {'success': True, 'data': [u.serialize() for u in users]}
    return json.dumps(res), 200

# POST user
@app.route('/api/users/', methods=['POST'])
def make_user():
    post_body = json.loads(request.data)
    username = post_body.get('username')
    newUser = User(
        username=username
    )
    db.session.add(newUser)
    db.session.commit()
    return json.dumps({'success': True, 'data': newUser.serialize()}), 201

# DELETE user
@app.route('/api/user/<int:user_id>/', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return json.dumps({'success': False, 'error': 'User not found'}), 404
    db.session.delete(user)
    db.session.commit()
    return json.dumps({'success': True, 'data': user.serialize()}), 200

# GET comments
@app.route('/api/comments/', methods=['GET'])
def get_comments():
    comments = Comment.query.all()
    res = {'success': True, 'data': [c.serialize() for c in comments]}
    return json.dumps(res), 200

# POST comment
@app.route('/api/comments/<int:post_id>/', methods=['POST'])
def post_comment(post_id):
    post_body = json.loads(request.data)
    body_comment = post_body.get('body')
    username = post_body.get('username')
    user = User.query.filter_by(username=username).first()
    user_id = user.id
    newComment = Comment(
        body_comment=body_comment,
        time_stamp=format(datetime.datetime.now()),
        user_id=user_id,
        post_id=post_id
    )
    db.session.add(newComment)
    db.session.commit()
    return json.dumps({'success': True, 'data': newComment.serialize()}), 201


"""
YOUR ROUTES BELOW
"""


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
