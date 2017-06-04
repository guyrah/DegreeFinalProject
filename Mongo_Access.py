from pymongo import MongoClient
from bson.json_util import dumps
import Reviews_Utils

def get_tagged_data(mongo_url, tgt_path):
    client = MongoClient(mongo_url)
    db = client.project77DB

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

def get_sequences(mongo_url):
    client = MongoClient(mongo_url)
    db = client.project77DB

    cursor = db.reviews.find({"private_id": {"$gt":0, "$lt":1001}, "fast_rank":{"$exists":False}}).sort("private_id",1)
    curr_index = -2

    for i in cursor:
        if curr_index + 1 < i['private_id']:
            print curr_index
            print i['private_id'], '-',

        curr_index = i['private_id']

def get_possible_values(mongo_url):
    final_result = dict()

    client = MongoClient(mongo_url)
    db = client.project77DB
    cursor = db.restaurants.find()
    for doc in cursor:
        final_result['']
        print doc


def load_restaurants(jsons, mongo_url):
    client = MongoClient(mongo_url)
    db = client.project77DB
    restaurants = db.restaurants_guy

    for json in jsons:
        restaurants.insert(json)


def get_restaurants_summed_score(mongo_url):
    client = MongoClient(mongo_url)
    db = client.project77DB
    cursor = db.reviews_sunny.find()
    restaurants_collection = db.restaurants_guy

    errors = 0
    restaurants = dict()

    for i, doc in enumerate(cursor):
        if not restaurants.has_key(doc['business_id']):
            restaurants[doc['business_id']] = dict()
            restaurants[doc['business_id']]['big_dish_rank'] = dict()
            restaurants[doc['business_id']]['quality_of_service_rank'] = dict()
            restaurants[doc['business_id']]['fast_rank'] = dict()
            restaurants[doc['business_id']]['food_quality_rank'] = dict()

        try:
            restaurants[doc['business_id']]['big_dish_rank'][str(doc['big_dish_rank'])] = \
            restaurants[doc['business_id']]['big_dish_rank'].get(str(doc['big_dish_rank']), 0) + 1
            restaurants[doc['business_id']]['quality_of_service_rank'][doc['quality_of_service_rank']] = \
            restaurants[doc['business_id']]['quality_of_service_rank'].get(doc['quality_of_service_rank'], 0) + 1
            restaurants[doc['business_id']]['fast_rank'][doc['fast_rank']] = \
            restaurants[doc['business_id']]['fast_rank'].get(doc['fast_rank'], 0) + 1
            restaurants[doc['business_id']]['food_quality_rank'][doc['qualityrank']] = \
            restaurants[doc['business_id']]['food_quality_rank'].get(doc['qualityrank'], 0) + 1
        except:
            errors += 1

        print i
        if i > 100:
            break
    big_dish_min = 1000000
    big_dish_max = -100000
    quality_of_serive_min = 100000
    quality_of_serive_max = -100000
    fast_rank_min = 100000
    fast_rank_max = -100000
    food_quality_rank_min = 100000
    food_quality_rank_max = -100000

    restaurants_stats = dict()

    for k1, v1 in restaurants.iteritems():
        if not restaurants_stats.has_key(k1):
            restaurants_stats[k1] = dict()

        restaurants_stats[k1]['big_dish_avg'] = v1['big_dish_rank']['1']



    return restaurants



mongo_url = 'mongodb://193.106.55.77:27017'


restaurant_business_file = '/home/osboxes/Desktop/yelp_dataset/yelp_academic_dataset_business.json'
restaurant_reviews_file = '/home/osboxes/Desktop/yelp_dataset/yelp_academic_dataset_review.json'
restaurant_business_ids_path = '/home/osboxes/Desktop/yelp_dataset/resturant_business_ids.txt'
restaurant_reviews_sample_file = 'reviews_sample.txt'

#restaurant_ids = Reviews_Utils.get_restaurant_business_id(restaurant_business_file,restaurant_business_ids_path)
#count_restaurant_reviews(restaurant_reviews_file, restaurant_ids)

#load_restaurants(Reviews_Utils.get_business_json('/home/osboxes/Desktop/yelp_dataset/yelp_academic_dataset_business.json', restaurant_ids), mongo_url)
#get_possible_values(mongo_url)

get_restaurants_summed_score(mongo_url)