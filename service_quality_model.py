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
from sklearn.svm import SVC

src_path = 'tagged_data.json'
#data_path = 'sample_tagged_data.json'
data_field = 'text'
target_field = 'quality_of_service_rank'
class_map = {0: 0,
             1: 1,
             # 2: 2,
             3: 3}


feature_extraction_config = {
            'text_to_vector_uni_vocabulary': ['vocabularies/text_to_vector_uni_vocabulary_10.txt',
                                              'vocabularies/text_to_vector_uni_vocabulary_20.txt',
                                              'vocabularies/text_to_vector_uni_vocabulary_-1.txt',
                                              'vocabularies/text_to_vector_vocabulary.txt'],
            'text_to_vector_bi_vocabulary': ['vocabularies/text_to_vector_bi_vocabulary.txt'],
            'tf_idf_vector': [True, False],
            'counter_vector': [True, False],
            'binary_vector': [True,False],
            'best_representing_words_list': ['vocabularies/service_best_words.txt',
                                             'vocabularies/service_best_words_10.txt',
                                             'vocabularies/service_best_words_12.txt',
                                             'vocabularies/service_best_words_20.txt'],
            'surrounding_words': [True, False],
            'polarity_vocabulary': 'vocabularies/polarity_words.txt',
            'positive_words_count': [True, False],
            'negative_words_count': [True, False],
            'polarity_count': [True, False],
            'parts_of_speech': [True, False],
            'uni_gram': [True, False],
            'bi_gram': [True, False],
            'not_count': [True, False]
        }
train_model.get_best_config(src_path=src_path, data_field=data_field, target_field=target_field, feature_extraction_config=feature_extraction_config, class_map=class_map)
'''
class_map = {0: 0,
             1: 1,
             # 2: 2,
             3: 3}

# Prepare vocabularies
text_to_vector_uni_vocabulary = vocabularies.read_vocabulary('vocabularies/text_to_vector_uni_vocabulary_10.txt')
#text_to_vector_uni_vocabulary = vocabularies.read_vocabulary('text_to_vector_uni_vocabulary.txt')
text_to_vector_bi_vocabulary = vocabularies.read_vocabulary('vocabularies/text_to_vector_bi_vocabulary.txt')
best_representing_words = vocabularies.read_best_words_list('vocabularies/service_best_words_costume.txt')
polarity_vocabulary = vocabularies.read_polarity_vocabulary('vocabularies/polarity_words.txt')


feature_extraction_config = {
    'text_to_vector_uni_vocabulary': text_to_vector_uni_vocabulary,
    'text_to_vector_bi_vocabulary': text_to_vector_bi_vocabulary,
    'tf_idf_vector': False,
    'counter_vector': True,
    'binary_vector': False,
    'best_representing_words_list': best_representing_words,
    'surrounding_words': True,
    'polarity_vocabulary': polarity_vocabulary,
    'positive_words_count': True,
    'negative_words_count': True,
    'polarity_count': True,
    'parts_of_speech': True,
    'uni_gram': True,
    'bi_gram': False,
    'not_count': False
}

data, target, original_text = train_model.prepare_data(src_path=src_path,
                                        data_field=data_field,
                                        target_field=target_field,
                                        class_map=class_map,
                                        balance_classes=False,
                                        randomize=False,
                                        feature_config=feature_extraction_config)

clf = SVC(kernel='linear', degree=3)
#clf = tree.DecisionTreeClassifier(max_depth=5)

train_model.test_model(clf, data, target, original_text, 'service_quality_mistakes.csv')
'''