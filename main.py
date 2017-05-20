import train
import Mongo_Access
import NLP_Utils
from Logger import Logger
from config import *
#region Config:

REFRESH_TAGGED_DATA = False
MONGO_URL = 'mongodb://193.106.55.77:27017'
DATA_PATH = "tagged_data.json"
VOCABULARY_PATH = 'vocabulary.txt'
DATA_FIELD = 'text'
TESTSET_SIZE = 10

#endregion

def refreshTaggedData():
    Mongo_Access.get_tagged_data(MONGO_URL, DATA_PATH)
    NLP_Utils.json_stats_counter(DATA_PATH)
    NLP_Utils.create_vocabulary(DATA_PATH, VOCABULARY_PATH)


def __main__():
    Logger.log_info("Starting script...")

    if REFRESH_TAGGED_DATA:
        print "Refreshing tagged data..."
        refreshTaggedData()
        print "Finished refreshing tagged data"
    else:
        print "Not refreshing tagged data"

    #mode = vectorMode.binary
    for mode in vectorMode.modes:
        Logger.log_info("mode: " + mode)
        train.train_qualityrank(DATA_PATH, DATA_FIELD, VOCABULARY_PATH, TESTSET_SIZE, mode)

    print "Finished"





__main__()