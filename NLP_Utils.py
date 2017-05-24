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


def json_to_csv(src_path, tgt_path):
    fields = ['review_id', 'qualityrank','quality_of_service_rank',\
              'fast_rank','price_rank','big_dish_rank',\
              'value_for_money_rank','clean_rank',\
              'good_for_vegan_rank','good_for_meat_rank']

    with open(src_path,'r') as src_file:
        with open(tgt_path, 'w') as tgt_file:
            tgt_file.write(','.join(fields) + '\n')

            # Runns on each line - which supposed to be a doc
            for line in src_file:
                current_json = json.loads(line)
                current_fields = list()
                for f in fields:
                    current_fields.append(str(current_json.get(f,'')))

                tgt_file.write(','.join(current_fields) + '\n')


def prepare_tagged_data_to_train(src_path,
                                 data_field,
                                 target_field,
                                 vocabulary,
                                 class_map=None):
    """
       fields = ['review_id', 'qualityrank','quality_of_service_rank',\
                 'fast_rank','price_rank','big_dish_rank',\
                 'value_for_money_rank','clean_rank',\
                 'good_for_vegan_rank','good_for_meat_rank']
    """
    with open(src_path, 'r') as src_file:
        filtered_count = 0
        data = list()
        target = list()
        # Runns on each line - which supposed to be a doc
        for line in src_file:
            current_json = json.loads(line)
            if current_json.has_key(target_field):
                # If no filter is asked
                if (class_map == None):
                    data.append(text_to_hot_vector(current_json[data_field], vocabulary))
                    target.append(int(current_json[target_field]))
                # If filter is needed
                else:
                    # Check if json is valid according to filter
                    if (int(current_json[target_field]) in class_map):
                        data.append(text_to_hot_vector(current_json[data_field], vocabulary))
                        target.append(class_map[int(current_json[target_field])])
                    # If filtered a json
                    else:
                        filtered_count += 1

        print 'filtered: ', filtered_count
        return data, target


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