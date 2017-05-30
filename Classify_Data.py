import sys
from sklearn.externals import joblib
import Mongo_Access
import Sunny_NLP_Utils
import sunny_featuresExtractor
from datetime import datetime
from pymongo import MongoClient
from bson.json_util import dumps
import simplejson as json
import time
import threading
from threading import Thread
import Queue

#region config
mongoDbURL = 'mongodb://193.106.55.77:27017'
mongoDbHost = "193.106.55.77"
mongoDbPort = 27017

#reviews_collection = "reviews_sunny"
reviews_collection = "reviews_threading"
restaurant_collection = "restaurants_sunny"

review_ids_to_update_path = "models/ids_to_update.json"
rest_ids_path = "models/rest_ids.txt"
vocabulary_path = "models/vocabulary_for_example_models.txt"
vocabulary = Sunny_NLP_Utils.read_vocabulary(vocabulary_path)
jsonDataField = "text"
jsonPrivateIdField = "private_id"
_db = None
_logfile = None
_log_file_name = "models/logs_threading.txt"
_reviews_jsons = None
_reviews_bulk = None
_count_success = None
_count_failed = None
_get_reviews_lock = threading.Lock()
_counters_lock = threading.Lock()
_log_lock = threading.Lock()
_logs_queue = None
#endregion

#region log
def init_logger():
    global _logs_queue

    if not _logs_queue:
        _logs_queue = Queue.Queue()

    t = Thread(target=log_queue)
    t.setDaemon(True)
    t.setName("logger")
    t.start()

def log_queue():
    global _logs_queue

    while True:
        message = _logs_queue.get(True)
        log_to_file(message)
        _logs_queue.task_done()

def log_to_file(message):
    global _log_file_name
    with open(_log_file_name, "a+") as f:
        f.write(message)


def log(message):
    global _logs_queue
    thread_name = str(threading.current_thread().getName())
    n_message = str(datetime.now()) + " Thread: " + thread_name + " message: " + message + "\n"
    _logs_queue.put(n_message)

"""
def log(message):
    thread_name = str(threading.current_thread().getName())
    n_message = str(datetime.now()) + " Thread: " + thread_name + " message: " + message + "\n"
    t = Thread(target=log_async,args=(n_message , ))
    t.setDaemon(True)
    t.start()

def log_async(message):
    global _logfile

    with _log_lock:
        if not _logfile:
            _logfile = open(_log_file_name, "a+")
        #print message
        _logfile.write(message)
        _logfile.flush()
"""
#endregion

#region review_multi_threaded

def count(flag):
    global _count_success
    global _count_failed
    with _counters_lock:
        if not _count_success:
            _count_success = 0
            _count_failed = 0
        if flag == "success":
            _count_success += 1
        elif flag == "fail":
            _count_failed += 1


def load_reviews_jsons(num_of_reviews):
    global _reviews_jsons
    global _reviews_bulk
    if not _reviews_jsons:
        _reviews_bulk = 0
        if num_of_reviews > 0:
            _reviews_jsons = []
            with open(review_ids_to_update_path, 'r') as ids_to_update_file:
                line_count = 0
                for line in ids_to_update_file:
                    _reviews_jsons.append(line)
                    line_count += 1
                    if line_count == num_of_reviews:
                        log("Loaded " + str(num_of_reviews) + " reviews from file to memory")
                        break
        else:
            with open(review_ids_to_update_path, 'r') as ids_to_update_file:
                _reviews_jsons = ids_to_update_file.readlines()
                log("Loaded all reviews from file to memory")


def tag_reviews_multi(num_of_reviews, num_of_threads, bulk_size, labels):
    log("Tagging reviews with threading")
    log("Config : threads=" + str(num_of_threads) + " reviews_to_tag=" + str(num_of_reviews) + " bulk_size=" + str(bulk_size))

    #loading models
    models = load_models(labels)

    # loading all reviews ids to memory
    load_reviews_jsons(num_of_reviews)

    threads = []
    for i in range(1, num_of_threads + 1):
        t = Thread(target=thread_tagger,args=(bulk_size, models, ))
        t.setName("t" + str(i))
        t.setDaemon(True)
        threads.append(t)

    # starting all threads
    for thr in threads:
        thr.start()
        log("Started thread: " + thr.getName())

    # waiting for all threads to start
    for thr in threads:
        thr.join()
    log("All threads finished...")
    log("Tagged " + str(_count_success) + " reviews succesfully")
    log("Failed to tag " + str(_count_failed) + " reviews")


def get_bulk_ids(bulk_size):
    global _reviews_jsons
    global _reviews_bulk
    with _get_reviews_lock:
        ids_to_return = _reviews_jsons[_reviews_bulk: _reviews_bulk + bulk_size]
        _reviews_bulk += bulk_size
        log("Sent bulk review ids: " + str(_reviews_bulk) + "-" + str(_reviews_bulk + bulk_size))
        return ids_to_return

def thread_tagger(bulk_size, models):
    try:
        slave(bulk_size, models)
    except:
        log("Exception in slave thread: " + str(sys.exc_info()))

def slave(bulk_size, models):
    log("Started to work...")
    json_reviews = get_bulk_ids(bulk_size)
    private_id = None
    tag_res = True

    while(len(json_reviews) > 0):
        for review_json in json_reviews:
            try:
                private_id = None
                current_json = json.loads(review_json)
                if (current_json.has_key(jsonDataField)):

                    # extract review from json
                    review = current_json[jsonDataField]

                    # getting private id
                    private_id = current_json[jsonPrivateIdField]

                    # checking if the review text is ascii
                    if all(ord(char) < 128 for char in review):

                        tag_res = tag_review(private_id=private_id, models=models, review=review, save_to_Db = True)
                        if tag_res:
                            log("Tagged review private id: " + str(private_id) + " succesfully")
                            count("success")
                        else:
                            log("Failed to tag review private id: " + str(private_id))
                            count("failed")
                    else:
                        log("Review private id: " + str(private_id) + " is not ascii")
                        count("fail")
            except:
                if not private_id:
                    private_id = "ERROR"
                log("Exception occred while working on private_id: " + str(private_id))

        # getting more reviews
        json_reviews = get_bulk_ids(bulk_size)

    log("Finished working, no more reviews to tag.")


#endregion

def get_connection():
    global _db
    if not _db:
        client = MongoClient(host=mongoDbHost, port=mongoDbPort, maxPoolSize=100, minPoolSize=10)
        _db = client.project77DB
    return _db

def get_ids_to_update(mongo_url, tgt_path, limit):
    db = get_connection()

    if limit > 0:
        cursor = db[reviews_collection].find({"fast_rank":{"$exists": False}}, {jsonPrivateIdField  : "1", "business_id" : 1 , "text" : 1}).limit(limit)
    else:
        cursor = db[reviews_collection].find({"fast_rank": {"$exists": False}}, {jsonPrivateIdField : "1", "business_id": 1, "text": 1})

    with open(tgt_path, 'w+') as file:
        for i, doc in enumerate(cursor):
            file.write(dumps(doc) + '\n')

def get_label_config(label):
    config = {}
    config["target_field"] = label
    if label == "qualityrank":
        config["vocabulary"] = vocabulary
        config["mode"] = "binary"
        config["count_POS"] = False
        config["calc_polarity"] = False
        config["use_bestwords"] = False
        config["to_lower"] = True
    elif label == "fast_rank":
        config["vocabulary"] = vocabulary
        config["mode"] = "binary"
        config["count_POS"] = True
        config["calc_polarity"] = True
        config["use_bestwords"] = False
        config["to_lower"] = True
    return config

def text_to_feat_vector(text, config):
    vector = featuresExtractor.calcFeatures(text,config["vocabulary"],config["mode"],config["count_POS"],config["calc_polarity"], config["use_bestwords"], config["target_field"], config["to_lower"])
    return vector

def load_models(labels):

    # models path should look like models/*labelname_model.pkl
    models_paths = {}
    for label in labels:
        models_paths[label] = str("models/" + label + "_model.pkl")

    models = {}
    for label, filename in models_paths.iteritems():
        with open(filename, 'rb') as model_file:
             model = joblib.load(model_file)
             models[label] = model

    return models

def update_review(private_id, values):
    log("Updating review private id: " + str(private_id) +" with classified models inside the DB...")
    db = get_connection()

    # tagging each label in the DB according to model predictions
    for label, rank in values.iteritems():
        db[reviews_collection].update({jsonPrivateIdField  : private_id},
                                      { "$set" :
        {
            label : int(rank)
        }})

    # marking the review as tagged by the algorithm
    db[reviews_collection].update({jsonPrivateIdField : private_id},
                                  {"$set":
                                {
                                    "auto_tag" : 1
                                }})

def classify_reviews(models, num_of_reviews):
    global _reviews_jsons
    line_counter = 0
    errs_count = 0
    tag_res = True
    load_reviews_jsons(num_of_reviews)

    for line in _reviews_jsons:
        log("Working on line " + str(line_counter))

        current_json = json.loads(line)

        if (current_json.has_key(jsonDataField)):
            review = current_json[jsonDataField]
            if all(ord(char) < 128 for char in review):
                private_id = current_json[jsonPrivateIdField]

                tag_res = tag_review(private_id=private_id , models=models, review=review, save_to_Db = True)

                if tag_res == False:
                    errs_count += 1
            else:
                errs_count += 1
                log("Error : Review not in ascii format. num: " + str(errs_count))
        line_counter += 1


def tag_review(private_id, models, review, save_to_Db):
    values = dict()

    try:
        # Classifying review with every model
        for label, model in models.iteritems():
            log("Classifying review private_id : " + str(private_id) + " for category : " + label)
            cur_config = get_label_config(label)
            vector = text_to_feat_vector(review, cur_config)
            rank = model.predict(vector)
            # log("review tagged for label " + label + " as : " + str(rank))
            values[label] = rank
            if save_to_Db == True:
                update_review(private_id, values)
        return True
    except:
        log("Exception occured while tagging review " + str(private_id) + ". exception: " + str(sys.exc_info()))
        return False


"""
This function updates all the reviews in the DB with the rank according to the trained model
"""
def tag_all_reviews(labels, num_of_reviews):
    #{"qualityrank": "models/qualityrank_model.pkl", "fast_rank": "models/fast_rank_model.pkl"}

    log("loading models from files")
    models = load_models(labels)

    log("Getting reviews texts and ids to file : " + str(review_ids_to_update_path))
    # unmark this line to get the reviews to file system
    #get_ids_to_update(mongoDbURL, review_ids_to_update_path, 0)

    log("Starting to classify reviews")
    classify_reviews(models, num_of_reviews)

    log("Finished to classify reviews")


"""
This function updates the score for each restaurant with reviews
"""
def update_restuarants_ranks(labels):
    log("Starting to update restaurants")

    # remove this line if you want to re calculate the restaurants ids with reviews
    #read_restaurants_ids_with_reviews()

    with open(rest_ids_path,"r") as rest_ids:
        for line in rest_ids:
            rest_id = line.strip()
            log("Getting restaurant reviews sum for rest_id: " + rest_id)
            rest_rank_sum = get_rest_reviews_sum(rest_id, labels)
            normalize_rank_sum(rest_id, labels, rest_rank_sum)

"""
This function normalizes the sum rank to a number between 0 to 5 for each category
"""
def normalize_rank_sum(rest_id, labels, rest_rank_sum):
    #this dict contains a label for key and a tuple for value
    #the tuple is sum of reviews and number of reviews
    normalized_dict = {}

    for key, value in rest_rank_sum.iteritems():
        normalized_dict[key[0]] = normalized_dict.get([key[0]],(0,0)) + (key[1]* value, value)

    #calc average
        for label, sum_and_count in normalized_dict.iteritems():
            normalized_dict[key] = sum_and_count[0] / sum_and_count[1]

        log(str(normalized_dict))
        return

"""
This function read all the restaurants that have reviews to a file
"""
def read_restaurants_ids_with_reviews():
    log("Getting all ids of restaurants with reviews...")
    db = get_connection()

    cursor = db[restaurant_collection].find({} , {"business_id" : 1})
    with open(rest_ids_path, 'w+') as file:
        for i, doc in enumerate(cursor):
            business_id = doc["business_id"]
            log("Checking if restaurant " + business_id + " has reviews...")
            rest_reviews_count = db[reviews_collection].find({"business_id": business_id}).count()
            if (rest_reviews_count > 0):
                file.write(business_id + '\n')

"""
This function gets all the reviews of a specific restaurant id and calculates
how many reviews were tagged 3 ,2 ,1 ,0 for each label
"""
def get_rest_reviews_sum(rest_id, labels):
    rank_sum = dict()
    db = get_connection()
    cursor = db[reviews_collection].find({"business_id" : rest_id})

    for i, doc in enumerate(cursor):
        for label in labels:
            try:
                cur_rank = int(doc[label])
                rank_sum[(label,cur_rank)] = rank_sum.get((label,cur_rank), 0) + 1
            except:
                log("Sample not tagged...")

    return rank_sum

def main():
    try:
        init_logger()

        global _reviews_jsons

        log("starting script...")

        tag_reviews = True
        update_restaurants = False

        labels = ["qualityrank", "fast_rank"]

        if tag_reviews == True:
            log("Tagging all reviews in the DB")
            """
            log("Tagging single threaded...")
            start = datetime.now()
            tag_all_reviews(labels, 1000)
            end = datetime.now()
            dur = end - start
            log("Duration = " + str (dur))

            _reviews_jsons = None
            """
            log("Tagging multi threaded...")
            start = datetime.now()
            tag_reviews_multi(num_of_reviews=0, num_of_threads=10, bulk_size=1000, labels=labels)
            end = datetime.now()
            dur = end - start
            log("Duration = " + str(dur))

        if update_restaurants == True:
            log("Ranking restaurants according to tagged reviews")
            update_restuarants_ranks(labels)

        log("Finished script successfully.")
    except:
        log("**********Exception occured********** : " + str(sys.exc_info()))
        raise

main()