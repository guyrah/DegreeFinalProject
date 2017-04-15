from sklearn.svm import SVC
import NLP_Utils

data_path = 'tagged_data.json'
data_field = 'text'
target_field = 'quality_of_service_rank'
#target_field = 'qualityrank'
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
"""
a = dict()
for i in train_target:
    a[i] = a.get(i, 0) + 1

print a
"""

model = SVC(kernel='poly', degree=5, C=2.0)
model.fit(train_data, train_target)

print model.predict(test_data)
#print model.score(test_data, test_target)