import re
from stemming.porter2 import stem
import simplejson as json
from nltk.stem.porter import *

"""
initialize items once
"""
pattern1 = re.compile('[\W_]+')
pattern2 = re.compile('\'')
stemmer = PorterStemmer()

def remove_non_letters(str):
    return pattern1.sub(' ', pattern2.sub('', str))

def stem_word(word):
    return stemmer.stem(word)

"""
A vocabulray item containing
1. index for hot vector
2. freq in all training samples
"""
class VocabulrayItem:
    def __init__(self, index, frequency):
        self.index = index
        self.freq = frequency

    def get_index(self):
        return self.index

    def get_freq(self):
        return self.freq

"""
Gets path of vocabulary file and returns a vocabulary item
"""
def read_vocabulary(path):
    vocabulary = dict()

    with open(path, 'r') as file:
        for i, line in enumerate(file):
            line = line.split(',')
            vocabulary[str(line[0])] = VocabulrayItem(index=i, frequency=line[1])

    return vocabulary

"""
    Gets text and vocabulary and transfoms it to hot vector
"""
def text_to_hot_vector(text, vocabulary):
    hot_vector = [0] * len(vocabulary)
    word_counter = dict()
    words_not_in_vocabulary = 0

    for word in str(remove_non_letters(text)).split():
        word = stem_word(word)
        word_counter[word] = word_counter.get(word, 0) + 1

    for word, value in word_counter.iteritems():
        if vocabulary.has_key(word):
            hot_vector[vocabulary[word].get_index()] = float(word_counter[word]) #/ float(vocabulary[word].get_freq())
        else:
            words_not_in_vocabulary += 1


    return hot_vector


def create_vocabulary(src_file_path, dst_file_path, repetitions_thershold=-1):
    exceptions = 0

    with open(src_file_path,'r') as file:
        word_counter = dict()

        counter = 1
        #
        for line in file:
            line_contents = json.loads(line)

            try:
                for word in str(remove_non_letters(line_contents['text'])).split():
                    word = stem_word(word)
                    word_counter[word] = word_counter.get(word, 0) + 1
            except Exception as e:
                print e
                exceptions += 1

            counter += 1

    with open(dst_file_path, 'w') as file:
        for k, v in word_counter.items():
            if repetitions_thershold == -1:
                file.write(k + ',' + str(v) + '\n')
            else:
                if v > repetitions_thershold:
                    file.write(k + ',' + str(v) + '\n')

    print 'number of exceptions: ', exceptions

"""
    Gets text and vocabulary and transfoms it to vector
    with tf-idf
"""
def text_2_tf_idf_vector(text, vocabulary):
    hot_vector = [0] * len(vocabulary)
    word_counter = dict()
    words_not_in_vocabulary = 0

    for word in str(remove_non_letters(text)).split():
        word = stem_word(word)
        word_counter[word] = word_counter.get(word, 0) + 1

    for word, value in word_counter.iteritems():
        if vocabulary.has_key(word):
            hot_vector[vocabulary[word].get_index()] = float(word_counter[word]) / float(vocabulary[word].get_freq())
        else:
            words_not_in_vocabulary += 1

    return hot_vector

"""
    Gets text and vocabulary and transfoms it to vector
    with each cell counts number of repetitions of word
"""
def text_2_repetitions_vector(text, vocabulary):
    hot_vector = [0] * len(vocabulary)
    word_counter = dict()
    words_not_in_vocabulary = 0

    for word in str(remove_non_letters(text)).split():
        word = stem_word(word)
        word_counter[word] = word_counter.get(word, 0) + 1

    for word, value in word_counter.iteritems():
        if vocabulary.has_key(word):
            hot_vector[vocabulary[word].get_index()] = float(word_counter[word])
        else:
            words_not_in_vocabulary += 1

    return hot_vector


"""
    Gets text and vocabulary and transfoms it to vector
    each cell if word appeared
"""
def text_2_binary_vector(text, vocabulary):
    hot_vector = [0] * len(vocabulary)
    word_counter = dict()
    words_not_in_vocabulary = 0

    for word in str(remove_non_letters(text)).split():
        word = stem_word(word)
        word_counter[word] = word_counter.get(word, 0) + 1

    for word, value in word_counter.iteritems():
        if vocabulary.has_key(word):
            hot_vector[vocabulary[word].get_index()] = 1
        else:
            words_not_in_vocabulary += 1

    return hot_vector


def get_surrounding_words(text, core_words):
    reps = 0

    surrounding_words = []
    text = str(remove_non_letters(text)).split()

    for i,word in enumerate(text):
        word = stem_word(word)

        if word in core_words:
            reps += 1
            surrounding_words.extend(text[i-3:i+7])

    return " ".join(surrounding_words), reps


def prepare_text(text, config):
    prepared_text = list()

    if config['tf_idf_vector']:
        prepared_text.extend(text_2_tf_idf_vector(text, config['text_to_vector_vocabulary']))
    if config['counter_vector']:
        prepared_text.extend(text_2_repetitions_vector(text, config['text_to_vector_vocabulary']))
    if config['binary_vector']:
        prepared_text.extend(text_2_binary_vector(text, config['text_to_vector_vocabulary']))

    return prepared_text