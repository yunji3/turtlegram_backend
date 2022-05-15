from pymongo import MongoClient
client = MongoClient()
db = client.turtlegram

doc = {'name': 'bobby', 'age': 21}
db.users.insert_one(doc)