from pymongo import MongoClient
from bson.json_util import dumps


def get_tagged_data(mongo_url, tgt_path):
    client = MongoClient(mongo_url)
    db = client.app1

    #cursor = db.reviews.find({"fast_rank":{"$exists": True}})
    cursor = db.reviews.find({"fast_rank": {"$exists":True},
    "$or":[{"qualityrank": {"$ne":'0'}},
    {"qualityrank": {"$ne":'0'}},
    {"quality_of_service_rank": {"$ne":'0'}},
    {"fast_rank": {"$ne":'0'}},
    {"price_rank": {"$ne":'0'}},
    {"big_dish_rank": {"$ne":'0'}},
    {"value_for_money_rank": {"$ne":'0'}},
    {"$and":[{"clean_rank": {"$ne":'0'}}, {"clean_rank":{"$exists":True}}]},
    {"good_for_vegan_rank": {"$ne":'0'}},
    {"good_for_meat_rank": {"$ne":'0'}}]})

    print cursor.count(), 'tagged reviews'
    with open(tgt_path, 'w') as file:
        for i, doc in enumerate(cursor):
            file.write(dumps(doc) + '\n')

