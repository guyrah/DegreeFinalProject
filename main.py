import train
import Mongo_Access
import NLP_Utils
from Logger import Logger
from config import *
#region Config:



#endregion

def refreshTaggedData():
    Mongo_Access.get_tagged_data(config.mongoDbURL, config.dataSetFilePath)
    NLP_Utils.json_stats_counter(config.dataSetFilePath)
    NLP_Utils.create_vocabulary(config.dataSetFilePath, config.VOCABULARY_PATH)


def __main__():

    Logger.log_info("Starting script...")

    # refreshing tagged data file if value set to true in config file
    if config.refreshTaggedData:
        print "Refreshing tagged data..."
        refreshTaggedData()
        print "Finished refreshing tagged data"
    else:
        print "Not refreshing tagged data"

    for mode in vectorMode.modes:
        Logger.log_info("mode: " + mode)
        train.train_qualityrank(config.dataSetFilePath, config.dataFieldName, config.VOCABULARY_PATH, mode)

        Logger.log_info("Finished")



__main__()