import NLP_Utils
from sklearn import tree
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import cross_val_predict
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score


data_path = 'tagged_data.json'
data_field = 'text'
target_field = 'quality_of_service_rank'
#target_field = 'qualityrank'
#target_field = 'value_for_money_rank'
vocabulary_path = 'vocabulary.txt'
from sklearn.svm import SVC

vocabulary = NLP_Utils.read_vocabulary(vocabulary_path)
data, target = NLP_Utils.prepare_tagged_data_to_train(src_path=data_path,
                                                      data_field=data_field,
                                                      target_field=target_field,
                                                      vocabulary=vocabulary,
                                                      filter_target_class=[0,1,3])

clf = tree.DecisionTreeClassifier()
#clf = clf.fit(train_data, train_target)
#clf = SVC(kernel='poly', degree=5, C=2.0)
predict = cross_val_predict(clf, data, target, cv=3)

print 'accuracy:', accuracy_score(target, predict)
print confusion_matrix(target, predict)

#scores = cross_val_score(clf, data, target, cv=10)
#print scores

