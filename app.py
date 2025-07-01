from flask import Flask, request, jsonify, render_template
from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from flask_cors import CORS
import hashlib
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)
CORS(app)
bcrypt = Bcrypt(app)

users = {}
comments = []

def generate_hash(username):
    salt = os.urandom(8).hex()
    hashed = hashlib.sha256((username + salt).encode()).hexdigest()
    return hashed, salt

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'message': '入力不備'}), 400
    if username in users:
        return jsonify({'message': '既に存在します'}), 400
    pw_hash = bcrypt.generate_password_hash(password).decode()
    hash_val, salt = generate_hash(username)
    users[username] = {'password': pw_hash, 'hash': hash_val, 'salt': salt}
    return jsonify({'message': '登録完了'})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    user = users.get(username)
    if not user or not bcrypt.check_password_hash(user['password'], password):
        return jsonify({'message': 'ログイン失敗'}), 401
    return jsonify({'message': 'ログイン成功', 'user': {'username': username, 'hash': user['hash']}})

@app.route('/api/comment', methods=['POST'])
def comment():
    data = request.json
    username = data.get('username')
    text = data.get('text')
    if not username or not text:
        return jsonify({'message': '無効なリクエスト'}), 400
    user = users.get(username)
    if not user:
        return jsonify({'message': 'ユーザーが見つかりません'}), 400
    comments.append({'username': username, 'text': text, 'hash': user['hash']})
    if len(comments) > 1000:
        comments.clear()
    return jsonify({'message': '投稿完了'})

@app.route('/api/comments', methods=['GET'])
def get_comments():
    return jsonify(comments)

if __name__ == '__main__':
    app.run(debug=True)
