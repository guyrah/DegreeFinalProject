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

data_path = 'tagged_data.json'
#data_path = 'sample_tagged_data.json'
data_field = 'text'
target_field = 'big_dish_rank'


class_map = {0: 0,
             1: 1,
             # 2: 2,
             3: 3}

# Prepare vocabularies
text_to_vector_uni_vocabulary = vocabularies.read_vocabulary('vocabularies/text_to_vector_uni_vocabulary_10.txt')
#text_to_vector_uni_vocabulary = vocabularies.read_vocabulary('text_to_vector_uni_vocabulary.txt')
text_to_vector_bi_vocabulary = vocabularies.read_vocabulary('vocabularies/text_to_vector_bi_vocabulary.txt')
best_representing_words = vocabularies.read_best_words_list('vocabularies/dish_size_best_words_10.txt')
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

data, target, original_text = train_model.prepare_data(src_path=data_path,
                                        data_field=data_field,
                                        target_field=target_field,
                                        class_map=class_map,
                                        balance_classes=True,
                                        randomize=False,
                                        feature_config=feature_extraction_config)

clf = SVC(kernel='linear', degree=3)
#clf = tree.DecisionTreeClassifier(max_depth=5)
train_model.test_model(clf, data, target, original_text, 'dish_size_quality_mistakes.csv')
