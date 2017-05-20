from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from sklearn import tree
import NLP_Utils
import pydotplus

data_path = 'tagged_data.json'
data_field = 'text'
#target_field = 'quality_of_service_rank'
target_field = 'qualityrank'
#target_field = 'value_for_money_rank'
vocabulary_path = 'vocabulary.txt'

vocabulary = NLP_Utils.read_vocabulary(vocabulary_path)
data, target = NLP_Utils.prepare_tagged_data_to_train(src_path=data_path,
                             data_field=data_field,
                             target_field=target_field,
                             vocabulary=vocabulary)
#data, target = np.array(data), np.array(target)


train_data = data[:-10]
train_target = target[:-10]
test_data = data[-10:]
test_target = target[-10:]

a = dict()
for i in train_target:
    a[i] = a.get(i, 0) + 1

print a

clf = tree.DecisionTreeClassifier()
clf = clf.fit(train_data, train_target)
print list(clf.predict(test_data))
print test_target
print clf.score(test_data, test_target)
#dot_data = tree.export_graphviz(clf, out_file=None)
#graph = pydotplus.graph_from_dot_data(dot_data)
#graph.write_pdf('decision_tree.pdf')

'''
gnb = GaussianNB()
print gnb.fit(train_data, train_target).score(test_data, test_target)
print list(gnb.predict(test_data))
print test_target
'''

"""
model = SVC(kernel='poly', degree=5, C=2.0)
model.fit(train_data, train_target)

print model.predict(test_data)
print test_target
#print model.score(test_data, test_target)
"""

