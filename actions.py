from Mongo_Access import get_tagged_data
import NLP_Utils

def refresh_vocabulary():
    #mongo_url = 'mongodb://84.108.189.236:27017'
    mongo_url = 'mongodb://193.106.55.77:27017'
    data_path = "tagged_data.json"

    get_tagged_data(mongo_url, data_path)
    NLP_Utils.create_vocabulary(data_path, 'vocabulary2.txt', repetitions_thershold=10)
    NLP_Utils.json_stats_counter(data_path)