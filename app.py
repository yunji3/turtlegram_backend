from datetime import datetime, timedelta
from functools import wraps
import json
import hashlib
from unittest import result
from bson import ObjectId
from flask import Flask, abort, jsonify, request
from flask_cors import CORS
import jwt
from pymongo import MongoClient

SECRET_KEY = 'turtle'


app = Flask(__name__)
cors = CORS(app, resources={r'*': {'origins': '*'}})
client = MongoClient('localhost',27017)
db = client.turtlegram


def autorize(f):
    @wraps(f)
    def decorated_function():
        if not 'Authorization' in request.headers:
            abort(401)
        token = request.headers['Authorization']
        try:
            user = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        except:
            abort(401)
        return f(user)
    return decorated_function


@app.route("/")
@autorize
def hello_world(user):
    print(user)
    return jsonify({'message': 'success'})


@app.route("/signup", methods=["POST"])
def sign_up():
    data = json.loads(request.data)
    
    print(data.get('email'))
    print(data['password'])

    pw = data.get('password', None)
    hashed_password= hashlib.sha256(pw.encode('utf-8')).hexdigest()
    
    doc = {
        'email': data.get('email'),
        # 'password': data.get('password')
        'password' : hashed_password
    }
    user = db.users.insert_one(doc)
    
    return jsonify({'message': 'success','msg': '회원가입 되었습니다!'})

@app.route("/login", methods=["POST"])
def login():
    print(request)
    data = json.loads(request.data)
    print(data)

    email = data.get("email")
    password = data.get("password")
    hashed_password= hashlib.sha256(password.encode('utf-8')).hexdigest()
    print(hashed_password)

    result = db.users.find_one({
        'email' : email,
        'password' : hashed_password
    })
    print(result)

    if result is None:
        return jsonify({'message': '틀립니다'}), 401

    payload = {
        'id' : str(result["_id"]),
        'exp' : datetime.utcnow() + timedelta(seconds=60*60*24) # 로그인 24시간유지
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    
    print(token)

    return jsonify({'message': 'success', 'token':token})

@app.route("/getuserinfo", methods=["GET"])
@autorize
def get_user_info(user):
    result = db.users.find_one({
        '_id':ObjectId(user["id"])
    })
       
    print(result)

    return jsonify({'message': 'success', 'email':result["email"]})

  
@app.route("/article", methods=["POST"])
@autorize
def post_article(user):
    data = json.loads(request.data)
    print(data)

    db_user = db.users.find_one({
        '_id':ObjectId(user["id"])
    })
    now = datetime.now().strftime("%H:%M:%S")
    doc = {
        'title' : data.get('title', None),
        'content' : data.get('content', None),
        'user' : user['id'],
        'user_email' : db_user['email'],
        'time':now
    }
    print(doc)
    db.article.insert_one(doc)

    return jsonify({"message":"success"})

@app.route("/article", methods=["GET"])
def get_article():
    articles = list(db.article.find())
    for article in articles:
        article["_id"] = str(article["_id"])

    return jsonify({"message":"success", "articles":articles})

if __name__ =='__main__':
    app.run('0.0.0.0', port=5000, debug=True)


