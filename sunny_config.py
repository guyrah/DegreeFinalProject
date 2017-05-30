class vectorMode:
    tfidf = "tfidf"
    count = "count"
    binary = "binary"
    modes = [binary]

class logLevels:
    error = 0
    warn = 1
    info = 2
    debug = 3
    level = debug

class config:
    mongoDbURL = 'mongodb://193.106.55.77:27017'
    dataSetFilePath = "tagged_data.json"
    positiveWordsFileName= 'positive-words_raw.txt'
    negativeWordsFileName = 'negative-words_raw.txt'
    polarityDictFileName = 'polarity_words_vocabulary.txt'
    qualityRankImportantWordsFile = "quality-rank-important.txt"
    fastRankImportantWordsFile = "fast-rank-important.txt"
    bestWordsPath = 'best-words.txt'
    vocabularyFileName = 'vocabulary.txt'
    jsonFieldName = 'text' #the field name in the json
    testSetSize = 150
    refreshTaggedData = False
    remove_stopwords = False
    to_lower = True
