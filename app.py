import json
from flask import Flask, request
from db import db, Post, User, Comment
from datetime import datetime, date, timedelta
from sqlalchemy import desc, and_
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

# GET all posts from specific day
@app.route('/api/posts/date/<int:month>/<int:day>/<int:year>/', methods=['GET'])
def get_all_posts_date(month, day, year):
    str_month = str(month)
    str_day = str(day)
    str_year = str(year)
    str_date = str_year + str_month + str_day
    s_date = datetime.strptime(str_date, "%Y%m%d").date()
    posts = Post.query.filter_by(date=s_date)
    return json.dumps({'success': True, 'data': [p.serialize() for p in posts]}), 200

# GET the post that is saved from yesterday
@app.route('/api/save/', methods=['GET'])
def save_post():
    s_date = date.today() - timedelta(days=1)
    posts = Post.query.filter_by(date=s_date)
    post = Post.query.order_by(desc(Post.upvotes)).first()
    res = {'success': True, 'data': post.serialize()}
    return json.dumps(res), 200

# POST(create) a post
@app.route('/api/posts/', methods=['POST'])
def make_a_post():
    post_body = json.loads(request.data)
    body_post = post_body.get('body')
    username = post_body.get('username')
    user = User.query.filter_by(username=username).first()
    if not user:
        return json.dumps({'success': False, 'error': 'user not found'}), 404
    user_id = user.id
    newPost = Post(
        upvotes=0,
        body_post=body_post,
        time_stamp= datetime.now(),
        date=date.today(),
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
    if post.date != date.today():
        return json.dumps({'success': False, 'error': 'old posts are locked'}), 403
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
    user = User.query.filter_by(username=username).first()
    if user:
        return json.dumps({'success': False, 'error': 'user already exists'}), 403
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

# GET comments for a particular post
@app.route('/api/comments/<int:pid>/', methods=['GET'])
def get_post_comments(pid):
    comments = Comment.query.filter_by(post_id = pid)
    return json.dumps({'success': True, 'data': [p.serialize() for p in comments]}), 200

# POST comment
@app.route('/api/comments/<int:post_id>/', methods=['POST'])
def post_comment(post_id):
    post = Post.query.filter_by(id=post_id).first()
    if not post:
        return json.dumps({'success': False, 'error': 'Post not found'}), 404

    post_body = json.loads(request.data)
    body_comment = post_body.get('body')
    username = post_body.get('username')
    user = User.query.filter_by(username=username).first()
    if not user:
        return json.dumps({'success': False, 'error': 'user not found'}), 404
    user_id = user.id
    newComment = Comment(
        body_comment=body_comment,
        time_stamp= datetime.now(),
        date=date.today(),
        user_id=user_id,
        post_id=post_id
    )
    db.session.add(newComment)
    db.session.commit()
    return json.dumps({'success': True, 'data': newComment.serialize()}), 201

# DELETE comment
@app.route('/api/comments/<int:comment_id>/', methods=['DELETE'])
def delete_comment(comment_id):
    comment = Comment.query.filter_by(id=comment_id).first()
    if not comment:
        return json.dumps({'success': False, 'error': 'Comment not found'}), 404
    db.session.delete(comment)
    db.session.commit()
    return json.dumps({'success': True, 'data': comment.serialize()}), 200

# UPDATE comment
@app.route('/api/comments/update/<int:comment_id>/', methods=['POST'])
def edit_comment(comment_id):
    comment = Comment.query.filter_by(id=comment_id).first()
    if not comment:
        return json.dumps({'success': False, 'error': 'Comment not found'}), 404
    post_body = json.loads(request.data)
    body_comment = post_body.get('body')
    comment.body_comment = body_comment
    db.session.commit()
    return json.dumps({'success': True, 'data': comment.serialize()}), 200


"""
YOUR ROUTES BELOW
"""


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
