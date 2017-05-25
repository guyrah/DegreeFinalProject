import train_model
import vocabularies

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
vocabulary_path = 'text_to_vector_vocabulary.txt'
from sklearn.svm import SVC

class_map = {0: 0,
             1: 1,
             # 2: 2,
             3: 3}

# Prepare vocabularies
text_to_vector_vocabulary = vocabularies.read_vocabulary('text_to_vector_vocabulary.txt')
best_representing_words = vocabularies.read_best_words_list('service_best_words.txt')

feature_extraction_config = {
    'tf_idf_vector': False,
    'counter_vector': True,
    'binary_vector': False,
    'surrounding_words': True,
    'best_representing_words_list': best_representing_words,
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
