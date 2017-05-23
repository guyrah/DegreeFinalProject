class vectorMode:
    tfidf = "tfidf"
    count = "count"
    binary = "binary"
    modes = [tfidf,count,binary]

class logLevels:
    error = 0
    warn = 1
    info = 2
    debug = 3
    level = debug

class config:
    mongoDbURL = 'mongodb://193.106.55.77:27017'
    dataSetFilePath = "tagged_data.json"
    VOCABULARY_PATH = 'vocabulary.txt'
    dataFieldName = 'text'
    testSetSize = 100
    refreshTaggedData = False
