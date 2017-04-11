from pymongo import MongoClient
from bson.json_util import dumps


def get_tagged_data():
    client = MongoClient("mongodb://84.108.189.236:27017")
    db = client.app1

    cursor = db.reviews.find({"fast_rank":{"$exists": True}})
    print cursor.count()
    with open("tagged_data.txt", 'w') as file:
        for i, doc in enumerate(cursor):
            file.write(dumps(doc) + '\n')