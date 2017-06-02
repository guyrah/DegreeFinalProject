import re
from sklearn import tree
from stemming.porter2 import stem
import simplejson as json
import random
from nltk.stem.porter import *
import nltk
from nltk.corpus import stopwords
from sunny_config import *

"""
initialize items once
"""
pattern1 = re.compile('[\W_]+')
pattern2 = re.compile('\'')
stemmer = PorterStemmer()

def calc_pos_rank(text):
    nouns_count = 0
    adjectives_count = 0
    verbs_count = 0
    pos_tags = nltk.pos_tag(nltk.word_tokenize(text))

    for word_token in pos_tags:
        if word_token[1][:2] == 'NN':
            nouns_count += 1
        elif word_token[1][:2] == 'JJ':
            adjectives_count += 1
        elif word_token[1][:2] == 'VB':
            verbs_count += 1

    return [nouns_count, adjectives_count, verbs_count]

def remove_non_letters(str):
    return pattern1.sub(' ', pattern2.sub('', str))

def remove_stopwords(text):
    new_text = ""
    for word in text.split():
        word = stem(word)
        if word not in stopwords.words('english'):
            new_text += word + " "
    new_text = new_text[0:-1]
    return new_text

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

    def toString(self):
        string = "index = " + str(self.index) + ", freq = " + str(self.freq)
        string = string.strip('\n')
        return string

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


def create_vocabulary(src_file_path, dst_file_path):
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
                    if(config.to_lower):
                        word = word.lower()
                    if(config.remove_stopwords):
                        word = remove_stopwords(word)
                    if(word != ''):
                        word_counter[word] = word_counter.get(word, 0) + 1
            except Exception as e:
                print e
                exceptions += 1

            counter += 1

            if counter > 1000:
                break

    with open(dst_file_path, 'w') as file:
        for k, v in word_counter.items():
            file.write(k + ',' + str(v) + '\n')

    print 'number of exceptions: ', exceptions


def create_vocabulary_tree(src_file_path, dst_file_path):
    exceptions = 0

    with open(src_file_path,'r') as file:
        word_counter = dict()

        counter = 1
        #
        for line in file:
            try:
                line_contents = json.loads(line)
                text_line = str(line_contents[config.jsonFieldName])
                text_line = remove_non_letters(text_line)

                for word in text_line.split():
                    word = stem_word(word)

                    if (config.remove_stopwords):
                        word = remove_stopwords(word)

                    if(config.to_lower):
                        word = word.lower()
                    if word != '':
                        word_counter[word] = word_counter.get(word, 0) + 1
            except Exception as e:
                print e
                exceptions += 1

            counter += 1

            if counter > 1000:
                break

    with open(dst_file_path, 'w') as file:
        for k, v in word_counter.items():
            file.write(k + ',' + str(v) + '\n')

    print 'number of exceptions: ', exceptions

def json_to_csv(src_path, tgt_path):
    fields = ['review_id', 'qualityrank','quality_of_service_rank',\
              'fast_rank','price_rank','big_dish_rank',\
              'value_for_money_rank','clean_rank',\
              'good_for_vegan_rank','good_for_meat_rank']

    with open(src_path,'r') as src_file:
        with open(tgt_path, 'w') as tgt_file:
            tgt_file.write(','.join(fields) + '\n')

            # Runs on each line - which supposed to be a doc
            for line in src_file:
                current_json = json.loads(line)
                current_fields = list()
                for f in fields:
                    current_fields.append(str(current_json.get(f,'')))

                tgt_file.write(','.join(current_fields) + '\n')

"""
def prepare_tagged_data_to_train(datasetFilePath, jsonFieldName, target_field, vocabulary, mode):
    "" "
       fields = ['review_id', 'qualityrank','quality_of_service_rank',\
                 'fast_rank','price_rank','big_dish_rank',\
                 'value_for_money_rank','clean_rank',\
                 'good_for_vegan_rank','good_for_meat_rank']
    "" "

    if (mode in vectorMode.modes):

        with open(datasetFilePath, 'r') as datasetFile:
            data = list()
            target = list()

            # Runs on each line - which supposed to be a doc
            for line in datasetFile:

                jsonCurrentSample = json.loads(line)
                if jsonCurrentSample.has_key(target_field):

                    vector = getVector(jsonCurrentSample[jsonFieldName], mode, vocabulary)
                    data.append(vector)
                    target.append(int(jsonCurrentSample[target_field]))

            return data, target
    else:
        raise ("Sunny - Invalid mode chosen.")



def json_stats_counter(src_path):
    fields = ['qualityrank','quality_of_service_rank',\
              'fast_rank','price_rank','big_dish_rank',\
              'value_for_money_rank','clean_rank',\
              'good_for_vegan_rank','good_for_meat_rank']
    stats_counter = dict()

    for f in fields:
        stats_counter[f] = [0] * 4


    with open(src_path,'r') as src_file:
        for line in src_file:
            current_json = json.loads(line)
            for f in fields:
                if current_json.has_key(f):
                    stats_counter[f][int(current_json[f])] = int(stats_counter.get(f,[0,0,0,0])[int(current_json[f])]) + 1

    for k,v in stats_counter.iteritems():
        print k, v

"""


def count_polarity_words(text, vocabulary):
    positive = 0
    negative = 0

    text = text.split()

    for word in text:
        word = stem_word(word)

        if word in vocabulary:
            if vocabulary[word] == 1:
                positive += 1
            else:
                negative += 1

    return positive, negative

def read_polarity_vocabulary(path):
    voc = dict()
    with open(path) as file:
        for line in file:
            k, v = line.split(',')
            voc[k] = int(v)

    return voc

def create_words_polarity_vocabulary(positive_path, negative_path, tgt_path):
    final_list = dict()

    with open(positive_path) as pos_file:
        for line in pos_file:
            final_list[stem_word(line.rstrip('\n'))] = 1

    with open(negative_path) as neg_file:
        for line in neg_file:
            final_list[stem_word(line.rstrip('\n'))] = -1

    with open(tgt_path, 'w') as tgt_file:
        for k, v in final_list.iteritems():
            tgt_file.write(k + ',' + str(v) + '\n')
"""

def create_best_words_list(data_path, data_field, target_field, save_path, vocabulary, number_of_words=10):
    # Gets the minimal max depth needed to get the wanted number of words

    #create_vocabulary_tree(config.dataSetFilePath, "tree_vocab.txt")
    #vocabulary = read_vocabulary("tree_vocab.txt")
    #vocabulary = read_vocabulary(config.vocabularyFileName)

    max_depth = 1
    members = 1
    while members < number_of_words:
        members += 2 ** max_depth
        max_depth += 1

    # Creates 2 classes - no refrence and there's refrence
    class_map = {0: 0,
                 1: 1,
                 2: 1,
                 3: 1}

    # Prepares data to train model
    data, target = train.prepare_data2(src_path=config.dataSetFilePath,
                                       jsonFieldName=config.jsonFieldName,
                                       target_field=target_field,
                                       vocabulary=vocabulary,
                                       mode=vectorMode.binary,
                                       class_map=class_map,
                                       count_POS=True,
                                       calc_polarity=True,
                                       useBestSurroundingWords=False,
                                       balance_classes=False)


    # Trains the model with the calculated depth
    clf = tree.DecisionTreeClassifier(max_depth=max_depth)
    clf.fit(data, target)

    # Gets top $number_of_words words
    a = clf.feature_importances_
    b = range(0, len(a))
    c = zip(a, b)
    c.sort(reverse=True)
    c = c[:number_of_words]

    # Prepares dict to transform int to words
    voc_list = [None] * len(vocabulary)
    for k, v in vocabulary.iteritems():
        voc_list[v.get_index()] = k

    # Write to file
    with open(save_path, 'w') as file:
        for value, i in c:
            word = voc_list[i]
            file.write(word + ',' + str(value) + '\n')


def get_surrounding_words(text, words_before=3, words_after=7):
    core_words = read_best_words_list(config.bestWordsPath)
    reps = 0

    surrounding_words = []
    text = str(remove_non_letters(text)).split()

    for i,word in enumerate(text):
        word = stem_word(word)

        if word in core_words:
            reps += 1
            if i < words_before:
                start_index = 0
            else:
                start_index = i - words_before

            if i +words_after >= len(text):
                end_index = len(text)
            else:
                end_index = i + words_after

            surrounding_words.extend(text[start_index:end_index])

    return " ".join(surrounding_words), reps
"""
"""
def read_best_words_list(path):
    best_words = list()

    with open(path,'r') as file:
        for line in file:
            best_words.append(str(line.split(',')[0]))

    return best_words
    
"""