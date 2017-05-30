import Sunny_NLP_Utils
from sunny_config import *

def calcFeatures(curr_text, vocabulary, mode, count_POS, calc_polarity, useBestWords, target_field, to_lower):

    if(to_lower):
        curr_text = curr_text.lower()

    featVector = getVector(curr_text, mode, vocabulary)

    if count_POS:
        pos_rank_result = Sunny_NLP_Utils.calc_pos_rank(curr_text)

        if len(curr_text.split()) > 0:
            curr_text_length = float(len(curr_text.split()))
            adj_count = float(pos_rank_result[1])
            ratio =  adj_count / curr_text_length
            ratio = int(ratio * 1000)
            pos_rank_result.append(ratio)

        featVector.extend(pos_rank_result)

    if calc_polarity:
        voc = Sunny_NLP_Utils.read_polarity_vocabulary(config.polarityDictFileName)
        pos_count, neg_count = Sunny_NLP_Utils.count_polarity_words(curr_text, voc)
        featVector.extend([pos_count,neg_count, pos_count-neg_count])
    """
    if useBestWords:
        text, reps = Sunny_NLP_Utils.get_surrounding_words(curr_text, config.bestWordsPath)
        featVector.extend([reps])
    """

    return featVector


"""
getting the correct vector according to the mode requested
"""
def getVector(curText, mode, vocabulary):

    vector = []
    if (mode == vectorMode.tfidf):
        vector = text_to_hot_vector(curText, vocabulary)
    elif (mode == vectorMode.binary):
        vector = text_to_binary_vector(curText, vocabulary)
    elif (mode == vectorMode.count):
        vector = text_to_count_vector(curText, vocabulary)
    return vector



"""
    Gets text and vocabulary and transfoms it to hot vector
"""
def text_to_hot_vector(text, vocabulary):
    hot_vector, word_counter = initVectorVars(len(vocabulary), text)
    words_not_in_vocabulary = 0

    for word, value in word_counter.iteritems():
        if vocabulary.has_key(word):
            hot_vector[vocabulary[word].get_index()] = float(word_counter[word]) / float(vocabulary[word].get_freq())
        else:
            words_not_in_vocabulary += 1

    return hot_vector

"""

Written by: Sunny 
"""
def text_to_binary_vector(text, vocabulary):
    binary_vector, word_counter = initVectorVars(len(vocabulary), text)

    for word, value in word_counter.iteritems():
        if vocabulary.has_key(word):
            if value > 0:
                binary_vector[vocabulary[word].get_index()] = 1
            else:
                binary_vector[vocabulary[word].get_index()] = 0

    return binary_vector

"""

Written by: Sunny 
"""
def text_to_count_vector(text, vocabulary):
    count_vector, word_counter = initVectorVars(len(vocabulary), text)

    for word, value in word_counter.iteritems():
        if vocabulary.has_key(word):
             count_vector[vocabulary[word].get_index()] = value


    return count_vector

def initVectorVars(vocabularyLength, text):
    vector = [0] * vocabularyLength
    word_counter = dict()
    word_counter = calcWordCountDict(text)
    return vector, word_counter

def calcWordCountDict(text):
    word_counter = dict()

    for word in str(Sunny_NLP_Utils.remove_non_letters(text)).split():
        word = Sunny_NLP_Utils.stem_word(word)
        word_counter[word] = word_counter.get(word, 0) + 1

    return word_counter