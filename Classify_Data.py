import vocabularies
import operator
import sys
from sklearn.externals import joblib
import feature_extraction_functions
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
#reviews_collection = "reviews_preprod"
#restaurant_collection = "restaurants_sunny"
restaurant_collection = "restaurants_prod"

review_ids_to_update_path = "models/Resources/ids_to_update.json"
rest_ids_path = "models/Resources/rest_ids.txt"
vocabulary_path = "models/Resources/vocabulary.txt"
__vocabulary = None
jsonDataField = "text"
jsonPrivateIdField = "private_id"

__category_service_quality_config = None
__category_dish_size_config = None
__category_food_quality_config = None
__category_food_speed_config = None

category_dish_size = "big_dish_rank"
category_service_quality = "quality_of_service_rank"
category_food_quality = "qualityrank"
category_food_speed = "fast_rank"

_db = None
_logfile = None
_log_file_name = "models/logs/logs2.txt"
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

#region filesystem

def load_vocabulary():
    vocabulary = dict()
    global __vocabulary
    if not __vocabulary:
        with open(vocabulary_path, 'r') as file:
            for i, line in enumerate(file):
                line = line.split(',')
                vocabulary[str(line[0])] = Sunny_NLP_Utils.VocabulrayItem(index=i, frequency=line[1])
        __vocabulary = vocabulary

#endregion

#region mongo

def get_connection():
    global _db
    if not _db:
        client = MongoClient(host=mongoDbHost, port=mongoDbPort, maxPoolSize=100, minPoolSize=10)
        _db = client.project77DB
    return _db

def load_reviews_to_fs(mongo_url, tgt_path, limit):
    db = get_connection()

    if limit > 0:
        cursor = db[reviews_collection].find({"fast_rank":{"$exists": False}}, {jsonPrivateIdField  : "1", "business_id" : 1 , "text" : 1}).limit(limit)
    else:
        cursor = db[reviews_collection].find({"fast_rank": {"$exists": False}}, {jsonPrivateIdField : "1", "business_id": 1, "text": 1})

    with open(tgt_path, 'w+') as file:
        for i, doc in enumerate(cursor):
            file.write(dumps(doc) + '\n')

def update_review(private_id, values):
    log("Updating review private id: " + str(private_id) + " with classified models inside the DB...")

    db = get_connection()

    # tagging each label in the DB according to model predictions
    for label, rank in values.iteritems():
        db[reviews_collection].update({jsonPrivateIdField: private_id},
                                      {"$set":
                                          {
                                              label: int(rank)
                                          }})

    # marking the review as tagged by the algorithm
    db[reviews_collection].update({jsonPrivateIdField: private_id},
                                  {"$set":
                                      {
                                          "auto_tag": 1,
                                      }})
#endregion

#region categories configurations

def __load_service_quality_config():
    global __category_service_quality_config
    if not __category_service_quality_config:
        config = {
            'text_to_vector_uni_vocabulary': 'vocabularies/text_to_vector_uni_vocabulary_10.txt',
            'text_to_vector_bi_vocabulary': 'vocabularies/text_to_vector_bi_vocabulary.txt',
            'tf_idf_vector': False,
            'counter_vector': True,
            'binary_vector': False,
            'best_representing_words_list': 'vocabularies/service_best_words_custom.txt',
            'surrounding_words': True,
            'polarity_vocabulary': 'vocabularies/polarity_words.txt',
            'positive_words_count': True,
            'negative_words_count': True,
            'polarity_count': True,
            'parts_of_speech': True,
            'uni_gram': True,
            'bi_gram': False,
            'not_count': False,
            'remove_stop_words': False
        }

        if config.has_key('polarity_vocabulary'):
            if isinstance(config['polarity_vocabulary'], str):
                config['polarity_vocabulary'] = vocabularies.read_polarity_vocabulary(
                    config['polarity_vocabulary'])
        if config.has_key('best_representing_words_list'):
            if isinstance(config['best_representing_words_list'], str):
                config['best_representing_words_list'] = vocabularies.read_best_words_list(
                    config['best_representing_words_list'])
        if config.has_key('text_to_vector_bi_vocabulary'):
            if isinstance(config['text_to_vector_bi_vocabulary'], str):
                config['text_to_vector_bi_vocabulary'] = vocabularies.read_vocabulary(
                    config['text_to_vector_bi_vocabulary'])
        if config.has_key('text_to_vector_uni_vocabulary'):
            if isinstance(config['text_to_vector_uni_vocabulary'], str):
                config['text_to_vector_uni_vocabulary'] = vocabularies.read_vocabulary(
                    config['text_to_vector_uni_vocabulary'])

        __category_service_quality_config = config

def __load_dish_size_config():
    global  __category_dish_size_config
    if not __category_dish_size_config:
        config = {
            'text_to_vector_uni_vocabulary': 'vocabularies/text_to_vector_uni_vocabulary_10.txt',
            'text_to_vector_bi_vocabulary': 'vocabularies/text_to_vector_bi_vocabulary.txt',
            'tf_idf_vector': False,
            'counter_vector': True,
            'binary_vector': False,
            'best_representing_words_list': 'vocabularies/dish_size_best_words_custom.txt',
            'surrounding_words': True,
            'polarity_vocabulary': 'vocabularies/polarity_words.txt',
            'polarity_count': True,
            'parts_of_speech': True,
            'uni_gram': True,
            'bi_gram': False,
            'not_count': False,
            'remove_stop_words': False
        }
        if config.has_key('polarity_vocabulary'):
            if isinstance(config['polarity_vocabulary'], str):
                config['polarity_vocabulary'] = vocabularies.read_polarity_vocabulary(
                    config['polarity_vocabulary'])
        if config.has_key('best_representing_words_list'):
            if isinstance(config['best_representing_words_list'], str):
                config['best_representing_words_list'] = vocabularies.read_best_words_list(
                    config['best_representing_words_list'])
        if config.has_key('text_to_vector_bi_vocabulary'):
            if isinstance(config['text_to_vector_bi_vocabulary'], str):
                config['text_to_vector_bi_vocabulary'] = vocabularies.read_vocabulary(
                    config['text_to_vector_bi_vocabulary'])
        if config.has_key('text_to_vector_uni_vocabulary'):
            if isinstance(config['text_to_vector_uni_vocabulary'], str):
                config['text_to_vector_uni_vocabulary'] = vocabularies.read_vocabulary(
                    config['text_to_vector_uni_vocabulary'])

        __category_dish_size_config = config

def __load_food_quality_config():
    global __category_food_quality_config
    if not __category_food_quality_config:
        config = {}
        config["target_field"] = category_food_quality
        config["vocabulary"] = __vocabulary
        config["mode"] = "binary"
        config["count_POS"] = True
        config["calc_polarity"] = False
        config["use_bestwords"] = False
        config["to_lower"] = False
        __category_food_quality_config = config

def __load_food_speed_config():
    global __category_food_speed_config
    if not __category_food_speed_config:
        config = {}
        config["target_field"] = category_food_speed
        config["vocabulary"] = __vocabulary
        config["mode"] = "binary"
        config["count_POS"] = False
        config["calc_polarity"] = False
        config["use_bestwords"] = False
        config["to_lower"] = True
        __category_food_speed_config = config

def load_configs():
    __load_dish_size_config()
    __load_food_quality_config()
    __load_food_speed_config()
    __load_service_quality_config()

def get_label_config(label):
    config = {}
    if label == category_food_speed:
        config = __category_food_speed_config
    elif label == category_food_quality:
        config =__category_food_quality_config
    elif label == category_dish_size:
        config = __category_dish_size_config
    elif label == category_service_quality:
        config = __category_service_quality_config
    else:
        raise Exception("Label does not exists exception in get_label_config")

    return config

#endregion

#region reviews
def text_to_feat_vector(text, config, label):
    # get vector according to Sunny's code
    if label in [category_food_quality, category_food_speed]:
        vector = sunny_featuresExtractor.calcFeatures(text,config["vocabulary"],config["mode"],config["count_POS"],config["calc_polarity"], config["use_bestwords"], config["target_field"], config["to_lower"])
    # get vector according to Guy's code
    elif label in [category_service_quality, category_dish_size]:
        vector = feature_extraction_functions.prepare_text(text, config)
    else:
        raise Exception("label error in text_to_feat_vector method")

    return vector

def load_models(labels):
    # models path should look like models/*labelname_model.pkl
    #calculating models file names
    models_paths = {}
    for label in labels:
        models_paths[label] = str("models/" + label + "_model.pkl")

    models = {}
    for label, filename in models_paths.iteritems():
        with open(filename, 'rb') as model_file:
             model = joblib.load(model_file)
             models[label] = model

    return models

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
            log("Getting config to classify review private_id : " + str(private_id) + " for category : " + label)
            cur_config = get_label_config(label)
            vector = text_to_feat_vector(review, cur_config, label)
            log("Classifying review private_id : " + str(private_id) + " for category : " + label)
            rank = model.predict(vector)
            values[label] = rank

        if save_to_Db:
            update_review(private_id, values)
        return True
    except:
        log("Exception occured while tagging review " + str(private_id) + ". exception: " + str(sys.exc_info()))
        return False
"""
This function updates all the reviews in the DB with the rank according to the trained model
"""
def tag_all_reviews(labels, num_of_reviews):
    log("loading models from files")

    models = load_models(labels)

    log("Starting to classify reviews")

    classify_reviews(models, num_of_reviews)

    log("Finished to classify reviews")

#endregion

#region Restaurants

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
            log("Trying to get restaurant reviews sum for rest_id: " + rest_id)
            rest_rank_sum, sum_of_reviews = get_rest_reviews_sum(rest_id, labels)

            if(len(rest_rank_sum) > 0):
                log("Normalizing reviews tags for rest_id: " + rest_id)
                normalized_dict = normalize_rank_sum(rest_id, labels, rest_rank_sum)
                update_restaurant_in_db(rest_id, normalized_dict, sum_of_reviews)

            else:
                log("There are no tagged reviews for rest_id: " + rest_id)

"""
This function gets all the reviews of a specific restaurant id and calculates
how many reviews were tagged 3 ,2 ,1 ,0 for each label
"""
def get_rest_reviews_sum(rest_id, labels):
    rank_sum = dict()
    db = get_connection()
    sum_of_reviews = 0
    cursor = db[reviews_collection].find({"business_id" : rest_id, "auto_tag" : 1})

    for i, doc in enumerate(cursor):
        cur_json = json.loads(dumps(doc))
        sum_of_reviews += 1

        for label in labels:
            try:
                cur_rank = int(cur_json[label])
                rank_sum[(label,cur_rank)] = rank_sum.get((label,cur_rank), 0) + 1
            except:
                log("Sample not tagged...")

    return rank_sum, sum_of_reviews

"""
This function normalizes the sum rank to a number between 0 to 5 for each category
"""
def normalize_rank_sum(rest_id, labels, rest_rank_sum):
    #this dict contains a label for key and a tuple for value
    #the tuple is sum of reviews and number of reviews
    normalized_dict = {}

    for key, value in rest_rank_sum.iteritems():
        if key[1] != 0:
            normalized_dict[key[0]] = tuple(map(operator.add, normalized_dict.get(key[0],(0,0)), (key[1]* value, value)))

    #calc average and normalize
    for label, sum_and_count in normalized_dict.iteritems():
        normalized_dict[label] = (float(sum_and_count[0]) / float(sum_and_count[1])) * 5.0 / 3.0

    log(str(normalized_dict))

    return normalized_dict

def update_restaurant_in_db(rest_id, normalized_dict, sum_of_reviews):
    log("Trying to update scores in DB for rest_id: " + str(rest_id))
    try:
        db = get_connection()

        for key, value in normalized_dict.iteritems():
            db_key = key.replace("rank", "score")
            log("Updating rest_id: " + str(rest_id) + " for label: "+str(db_key)+" with normalized value: " + str(value))
            db[restaurant_collection].update({"business_id" : rest_id},
                                          {"$set":
                                              {
                                                  db_key : value,
                                              }})
        db[restaurant_collection].update({"business_id": rest_id},
                                 {"$set":
                                     {
                                         "sum_of_reviews" : sum_of_reviews,
                                         "auto_tag": 1,
                                     }})
    except:
        log("Exception occured while trying to update rest_id: " + str(rest_id))

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

#endregion

def main():
    try:
        startTime = datetime.now()
        init_logger()
        log("starting script...")
        tag_reviews = False
        update_restaurants = True
        #labels = [category_food_quality, category_food_speed]
        labels = [category_food_quality, category_food_speed, category_service_quality, category_dish_size]

        if tag_reviews:
            #log("Getting reviews texts and ids from DB to file : " + str(review_ids_to_update_path))
            #load_reviews_to_fs(mongoDbURL, review_ids_to_update_path, 0)
            log("Loading vocabulary to memory...")
            load_vocabulary()
            log("Loading all categories configuratiosn to memory...")
            load_configs()
            log("Tagging all reviews and updating categories in the DB")
            #tag_all_reviews(labels, 1000)
            tag_reviews_multi(num_of_reviews=0, num_of_threads=25, bulk_size=1000, labels=labels)

        if update_restaurants:
            log("Ranking restaurants according to tagged reviews")
            update_restuarants_ranks(labels)

        log("Finished script successfully.")

        endTime = datetime.now()
        dur = endTime - startTime
        log("Script duration = " + str(dur))

    except:
        log("**********Fatal Exception Occurred********** : " + str(sys.exc_info()))
        raise

main()
