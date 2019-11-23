import json
from flask import Flask, request
from db import db, Post, User
import datetime

app = Flask(__name__)
db_filename = 'potd.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///%s' % db_filename
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

db.init_app(app)
with app.app_context():
    db.create_all()

post_id_counter = 0

comment_id_counter = 0

posts = {
}

comments = {

}
@app.route('/')
# GET all posts (time order)
@app.route('/api/posts/', methods=['GET'])
def get_all_posts():
    res = {'success': True, 'data': list(posts.values())}
    return json.dumps(res), 200

# GET all posts (upvote order)
@app.route('/api/posts/upvote/order/', methods=['GET'])
def get_all_posts_order():
    sort_posts = sorted(posts.items(), key=lambda e: e[1]['upvotes'])
    res = {'success': True, 'data': sort_posts}
    return json.dumps(res), 200

# POST(create) a post
@app.route('/api/posts/', methods=['POST'])
def make_a_post():
    global post_id_counter
    post_body = json.loads(request.data)
    title = post_body['title']
    body = post_body['body']
    username = post_body['username']
    newPost = {
        'id': post_id_counter,
        'upvotes': 1,
        'title': title,
        'body': body,
        'username': username,
        'timestamp': format(datetime.datetime.now())
    }
    posts[post_id_counter] = newPost
    post_id_counter += 1
    res = {'success': True, 'data': newPost}
    return json.dumps(res), 201

# GET a specific post
@app.route('/api/post/<int:post_id>/', methods=['GET'])
def get_a_post(post_id):
    post = posts.get(post_id, None)
    if not post:
        return json.dumps({'success': False, 'error': 'Post not found'}), 404
    return json.dumps({'success': True, 'data': post}), 200

# GET top post
@app.route('/api/post/top/', methods=['GET'])
def get_top_post():
    global posts
    max_upvote = 0
    max_post = []
    for i in range(len(posts)):
        post = posts[i]
        upvote = post['upvotes']
        if upvote > max_upvote:
            max_upvote = upvote
            max_post = post
    return json.dumps({'success': True, 'data': max_post}), 200

# DELETE a specific post
@app.route('/api/post/<int:post_id>/', methods=['DELETE'])
def delete_a_post(post_id):
    post = posts.get(post_id, None)
    if not post:
        return json.dumps({'success': False, 'error': 'Post not found'}), 404
    del posts[post_id]
    return json.dumps({'success': True, 'data': post}), 200

# GET comments for a specific post
@app.route('/api/post/<int:post_id>/comments/', methods=['GET'])
def get_comments(post_id):
    post = posts.get(post_id, None)
    if not post:
        return json.dumps({'success': False, 'error': 'Post not found'}), 404
    lst = []
    for c_id in comments.keys():
        if comments[c_id]['postID'] == post_id:
            comment = {
                'id': comments[c_id]['id'],
                'upvotes': comments[c_id]['upvotes'],
                'text': comments[c_id]['text'],
                'username': comments[c_id]['username'],
            }
            lst.append(comment)
    return json.dumps({'success': True, 'data': lst}), 200

# POST a comment for a specific post
@app.route('/api/post/<int:post_id>/comment/', methods=['POST'])
def post_a_comment(post_id):
    global comment_id_counter
    post_body = json.loads(request.data)
    text = post_body['text']
    username = post_body['username']
    newComment = {
        'id': comment_id_counter,
        'upvotes': 1,
        'text': text,
        'username': username,
        'postID': post_id,
    }
    comment = {
        'id': newComment['id'],
        'upvotes': newComment['upvotes'],
        'text': newComment['text'],
        'username': newComment['username'],
    }
    comments[comment_id_counter] = newComment
    comment_id_counter += 1
    res = {'success': True, 'data': comment}
    return json.dumps(res), 201

# POST an edited comment
@app.route('/api/post/<int:post_id>/comment/<int:comment_id>/', methods=['POST'])
def edit_a_comment(post_id, comment_id):
    post = posts.get(post_id, None)
    if not post:
        return json.dumps({'success': False, 'error': 'Post not found'}), 404
    oldComment = comments.get(comment_id, None)
    if not oldCcomment:
        return json.dumps({'success': False, 'error': 'Comment not found'}), 404
    post_body = json.loads(request.data)
    oldComment['text'] = post_body['text']
    comment = {
        'id': oldComment['id'],
        'upvotes': oldComment['upvotes'],
        'text': oldComment['text'],
        'username': oldComment['username'],
    }
    return json.dumps({'success': True, 'data': comment}), 200

# Upvote a post
@app.route('/api/post/<int:post_id>/upvote/', methods=['POST'])
def upvote_post(post_id):
    global posts
    post = posts.get(post_id, None)
    if not post:
        return json.dumps({'success': False, 'error': 'Post Not Found'}), 404
    post['upvotes'] = post['upvotes'] + 1
    return json.dumps({'success': True, 'data': post}), 200


"""
YOUR ROUTES BELOW
"""


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
