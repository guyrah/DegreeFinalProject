from sklearn import tree
import NLP_Utils
import json
import train_model


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


def create_vocabulary(src_file_path, dst_file_path, repetitions_thershold=-1):
    exceptions = 0

    with open(src_file_path,'r') as file:
        word_counter = dict()

        counter = 1
        #
        for line in file:
            line_contents = json.loads(line)

            try:
                for word in str(NLP_Utils.remove_non_letters(line_contents['text'])).split():
                    word = NLP_Utils.stem_word(word)
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


def read_best_words_list(path):
    best_words = list()

    with open(path,'r') as file:
        for line in file:
            best_words.append(str(line.split(',')[0]))

    return best_words

'''
    Creates best words vocabulary according to decision tree
'''
def create_best_words_list(data_path, data_field, target_field, save_path, config, number_of_words=10):
    # Gets the minimal max depth needed to get the wanted number of words
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
    data, target = train_model.prepare_data(src_path=data_path,
                                            data_field=data_field,
                                            target_field=target_field,
                                            class_map=class_map,
                                            balance_classes=False,
                                            randomize=False,
                                            feature_config=config)

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
    voc_list = [None] * len(config['text_to_vector_vocabulary'])
    for k, v in config['text_to_vector_vocabulary'].iteritems():
        voc_list[v.get_index()] = k

    # Write to file
    with open(save_path, 'w') as file:
        for value, i in c:
            file.write(voc_list[i] + ',' + str(value) + '\n')


def read_polarity_vocabulary(path):
    voc = dict()
    with open(path) as file:
        for line in file:
            k,v = line.split(',')
            voc[k] = int(v)

    return voc


def create_words_polarity_vocabulary(positive_path, negative_path, tgt_path):
    final_list = dict()

    with open(positive_path) as pos_file:
        for line in pos_file:
            final_list[NLP_Utils.stem_word(line.rstrip('\n'))] = 1

    with open(negative_path) as neg_file:
        for line in neg_file:
            final_list[NLP_Utils.stem_word(line.rstrip('\n'))] = -1

    with open(tgt_path, 'w') as tgt_file:
        for k,v in final_list.iteritems():
            tgt_file.write(k + ',' + str(v) + '\n')


def create_bi_vocabulary(src_file_path, dst_file_path, repetitions_thershold=-1):
    exceptions = 0

    with open(src_file_path,'r') as file:
        word_counter = dict()
        prev_word = None

        counter = 1
        #
        for line in file:
            line_contents = json.loads(line)

            try:
                for word in str(NLP_Utils.remove_non_letters(line_contents['text'])).split():
                    word = NLP_Utils.stem_word(word)
                    if prev_word is not None:
                        word_counter[prev_word + '-' + word] = word_counter.get(prev_word + '-' + word, 0) + 1

                    prev_word = word

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