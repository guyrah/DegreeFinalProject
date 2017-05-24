import random
import simplejson as json
import NLP_Utils
import pydotplus
from sklearn import tree
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import cross_val_predict
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestClassifier

data_path = 'tagged_data.json'
data_field = 'text'
target_field = 'quality_of_service_rank'
# target_field = 'qualityrank'
# target_field = 'value_for_money_rank'
vocabulary_path = 'vocabulary2.txt'
from sklearn.svm import SVC


def get_surrounding_words(text, core_words):
    reps = 0

    surrounding_words = []
    text = str(NLP_Utils.remove_non_letters(text)).split()

    for i, word in enumerate(text):
        word = NLP_Utils.stem_word(word)

        if word in core_words:
            reps += 1
            surrounding_words.extend(text[i - 3:i + 7])

    return " ".join(surrounding_words), reps


def get_best_words(clf, vocabulary, number_of_words=10):
    best_words = []
    a = clf.feature_importances_
    b = range(0, len(a))
    c = zip(a, b)
    c.sort()
    c = c[::-1]
    _, word_indexes = zip(*c[:number_of_words])

    voc_list = [None] * len(vocabulary)
    for k, v in vocabulary.iteritems():
        voc_list[v.get_index()] = k

    for i in word_indexes:
        best_words.append(voc_list[i])

    return best_words


def print_results(target, predict):
    conf_matrix = confusion_matrix(target, predict)
    print 'accuracy:', accuracy_score(target, predict)
    print conf_matrix

    for i, row in enumerate(conf_matrix):
        row_correct = 0
        row_error = 0
        for j, cell in enumerate(row):
            if j == i:
                row_correct += cell
            else:
                row_error += cell

        print str(i) + ':', str(row_correct / float(row_correct + row_error) * 100) + '%'


def service_prepare_tagged_data_to_train_from_path(src_path,
                                                   data_field,
                                                   target_field,
                                                   vocabulary,
                                                   class_map=None,
                                                   balance_classes=False,
                                                   randomize=False,
                                                   core_words=None):
    """
       fields = ['review_id', 'qualityrank','quality_of_service_rank',\
                 'fast_rank','price_rank','big_dish_rank',\
                 'value_for_money_rank','clean_rank',\
                 'good_for_vegan_rank','good_for_meat_rank']
    """

    if core_words is not None:
        print 'Getting surrounding words'

    with open(src_path, 'r') as src_file:
        data_dict = {}

        filtered_count = 0
        data = list()
        target = list()
        # Runns on each line - which supposed to be a doc
        for line in src_file:
            add_line = False
            current_json = json.loads(line)
            if current_json.has_key(target_field):
                # If no filter is asked
                if (class_map == None):
                    add_line = True
                # If filter is needed
                else:
                    # Check if json is valid according to filter
                    if (int(current_json[target_field]) in class_map):
                        add_line = True
                    # If filtered a json
                    else:
                        filtered_count += 1

            if add_line:
                data_dict[class_map[int(current_json[target_field])]] = data_dict.get(
                    class_map[int(current_json[target_field])], list())
                if core_words is None:
                    data_to_add = NLP_Utils.text_to_hot_vector(current_json[data_field], vocabulary)
                else:
                    text, reps = get_surrounding_words(current_json[data_field], core_words)
                    data_to_add = NLP_Utils.text_to_hot_vector(text, vocabulary)
                    data_to_add.append(reps)

                data_dict[class_map[int(current_json[target_field])]].append(data_to_add)

        if balance_classes:
            # gets the class with the least samples
            min_samples = -1
            for v in data_dict.itervalues():
                if min_samples == -1 or len(v) < min_samples:
                    min_samples = len(v)

            for k, v in data_dict.iteritems():
                if randomize:
                    random.shuffle(v)
                data.extend(v[:min_samples])
                target.extend([k] * min_samples)

            if randomize:
                c = list(zip(data, target))
                random.shuffle(c)
                data, target = zip(*c)
        else:
            for k, v in data_dict.iteritems():
                random.shuffle(v)
                data.extend(v)
                target.extend([k] * len(v))

        print 'filtered: ', filtered_count
        return data, target


vocabulary = NLP_Utils.read_vocabulary(vocabulary_path)
'''
sample = "One of my favorite dining spots in Toronto.  I've tried most of the menu items--the crab cakes are so-so too much filler not enough crab but the steak frites and calamari are excellent.  Pad Thai is ok but can be too sweet depending on who is making it.  Service is brisk and efficient.  Summer patio area can be unbearably hot at time it would be great if they could install some fans in the patio area."
class_map = {0: 0,
             1: 1,
             2: 1,
             3: 1}
data, target = service_prepare_tagged_data_to_train_from_path(src_path=data_path,
                                                    data_field=data_field,
                                                    target_field=target_field,
                                                    vocabulary=vocabulary,
                                                    class_map=class_map,
                                                    balance_classes=True,
                                                    randomize=False)

clf = tree.DecisionTreeClassifier(max_depth=6)
clf.fit(data, target)
service_words = get_best_words(clf, vocabulary=vocabulary)
'''
'''
class_map = {0: 0,
             1: 1,
             #2: 2,
             3: 3}

data, target = service_prepare_tagged_data_to_train_from_path(src_path=data_path,
                                                    data_field=data_field,
                                                    target_field=target_field,
                                                    vocabulary=vocabulary,
                                                    class_map=class_map,
                                                    balance_classes=False,
                                                    randomize=False,
                                                              core_words=None)

clf = tree.DecisionTreeClassifier(max_depth=6)
clf.fit(data, target)
clf = SVC(kernel='linear', degree=3)
# clf = GaussianNB()
# clf = RandomForestClassifier(max_depth=6)

predict = cross_val_predict(clf, data, target, cv=3)
print_results(target, predict)
'''
# surrounding_words = get_surrounding_words(sample, service_words)
# print service_words
# dot_data = tree.export_graphviz(clf, out_file=None)
# graph = pydotplus.graph_from_dot_data(dot_data)
# graph.write_pdf('decision_tree.pdf')

# scores = cross_val_score(clf, data, target, cv=10)
# print scores
''''''

class_map = {0: 0,
             1: 1,
             # 2: 2,
             3: 3}

import train_model

# Prepare vocabularies
text_to_vector_vocabulary = NLP_Utils.read_vocabulary('text_to_vector_vocabulary.txt')

feature_extraction_config = {
    'tf_idf_vector': False,
    'counter_vector': True,
    'binary_vector': False,
    'text_to_vector_vocabulary': text_to_vector_vocabulary
}

data, target = train_model.prepare_data(src_path=data_path,
                                        data_field=data_field,
                                        target_field=target_field,
                                        class_map=class_map,
                                        balance_classes=False,
                                        randomize=False,
                                        feature_config=feature_extraction_config)

clf = SVC(kernel='linear', degree=3)
train_model.test_model(clf, data, target)
