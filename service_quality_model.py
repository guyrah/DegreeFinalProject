import simplejson as json
import NLP_Utils
import pydotplus
from sklearn import tree
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import cross_val_predict
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score

data_path = 'tagged_data.json'
data_field = 'text'
target_field = 'quality_of_service_rank'
# target_field = 'qualityrank'
# target_field = 'value_for_money_rank'
vocabulary_path = 'vocabulary.txt'
from sklearn.svm import SVC


def service_prepare_tagged_data_to_train(src_path,
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
                    data.append(NLP_Utils.text_to_hot_vector(current_json[data_field], vocabulary))
                    target.append(int(current_json[target_field]))
                # If filter is needed
                else:
                    # Check if json is valid according to filter
                    if (int(current_json[target_field]) in class_map):
                        data.append(NLP_Utils.text_to_hot_vector(current_json[data_field], vocabulary))
                        target.append(class_map[int(current_json[target_field])])
                    # If filtered a json
                    else:
                        filtered_count += 1

        print 'filtered: ', filtered_count
        return data, target


vocabulary = NLP_Utils.read_vocabulary(vocabulary_path)
class_map = {0:0,
             1:1,
             2:1,
             3:1}
data, target = service_prepare_tagged_data_to_train(src_path=data_path,
                                                      data_field=data_field,
                                                      target_field=target_field,
                                                      vocabulary=vocabulary,
                                                      class_map=class_map)

# clf = tree.DecisionTreeClassifier(max_depth=3)
clf = tree.DecisionTreeClassifier()
# clf = clf.fit(train_data, train_target)
# clf = SVC(kernel='poly', degree=5, C=2.0)
predict = cross_val_predict(clf, data, target, cv=3)

print 'accuracy:', accuracy_score(target, predict)
print confusion_matrix(target, predict)

clf.fit(data, target)
dot_data = tree.export_graphviz(clf, out_file=None)
graph = pydotplus.graph_from_dot_data(dot_data)
graph.write_pdf('decision_tree.pdf')
# scores = cross_val_score(clf, data, target, cv=10)
# print scores
