import json
import random
import feature_extraction_functions

from sklearn.model_selection import StratifiedKFold
from sklearn.model_selection import cross_val_predict
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score

data_path = 'tagged_data.json'
data_field = 'text'
target_field = 'quality_of_service_rank'
# target_field = 'qualityrank'
# target_field = 'value_for_money_rank'

'''
    Prints predictions results
'''
def print_results(target, predict):
    conf_matrix = confusion_matrix(target, predict)
    print 'accuracy:', accuracy_score(target, predict)
    print conf_matrix

    for i, row in enumerate(conf_matrix):
        row_correct = 0
        row_error = 0
        for j, cell in enumerate(row):
            if j==i:
                row_correct += cell
            else:
                row_error += cell

        print str(i) + ':', str(row_correct / float(row_correct+row_error)*100) + '%'


def prepare_data(src_path,
                 data_field,
                 target_field,
                 class_map=None,
                 balance_classes=False,
                 randomize=False,
                 feature_config=None):
    """
       fields = ['review_id', 'qualityrank','quality_of_service_rank',\
                 'fast_rank','price_rank','big_dish_rank',\
                 'value_for_money_rank','clean_rank',\
                 'good_for_vegan_rank','good_for_meat_rank']
    """
    with open(src_path, 'r') as src_file:
        data_dict = {}
        filtered_count = 0

        data = list()
        target = list()
        orig_text = list()

        # Filters data only relevant data
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

            # Adds line if not filtered
            if add_line:
                data_dict[class_map[int(current_json[target_field])]] = data_dict.get(
                    class_map[int(current_json[target_field])], list())
                data_dict[class_map[int(current_json[target_field])]].append(current_json[data_field])

        # If balance_classes flag is true -
        # balances all classes according to the class with the least samples
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

        # If balance_classes flag is false -
        # add all examples to data and shuffle
        else:
            for k, v in data_dict.iteritems():

                if randomize:
                    random.shuffle(v)

                data.extend(v)
                target.extend([k] * len(v))

        # extract features from data
        for i, curr_text in enumerate(data):
            data[i] = feature_extraction_functions.prepare_text(curr_text, feature_config)
            orig_text.append(curr_text)


        #print 'filtered: ', filtered_count
        return data, target, orig_text


def test_model(clf, data, target, original_text=None ,mistakes_path=None):
    cv = StratifiedKFold(shuffle=True, random_state=2)
    predict = cross_val_predict(clf, data, target, cv=cv)
    print_results(target, predict)

    if mistakes_path is not None and original_text is not None:
        with open(mistakes_path, 'w') as file:
            file.write('true, predicted, text\n')
            for i, p in enumerate(predict):
                if p != target[i]:
                    try:
                        file.write(str(target[i]) + ',' + str(p) + ',' + original_text[i].replace('\n', '---').replace(',', ';') + '\n')
                    except Exception as e:
                        print original_text[i].replace('\n', '---').replace(',', ';')



