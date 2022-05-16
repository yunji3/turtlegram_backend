import json
import hashlib
from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient

client = MongoClient('localhost',27017)
db = client.turtlegram


app = Flask(__name__)
cors = CORS(app, resources={r'*': {'origins': '*'}})


@app.route("/")
def hello_world():
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

    # data = json.loads(request.data) # 자주 쓰일 스타일
    # print(data)
    # print(data.get('id'))
    # print(data["password"])
    

if __name__ =='__main__':
    app.run('0.0.0.0', port=5000, debug=True)


