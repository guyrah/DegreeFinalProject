import train_model

from sklearn import tree
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC

src_path = 'tagged_data.json'
data_field = 'text'
target_field = 'quality_of_service_rank'

def check_best_config():
    feature_extraction_config = {
                'text_to_vector_uni_vocabulary': ['vocabularies/text_to_vector_uni_vocabulary_10.txt',
                                                  'vocabularies/text_to_vector_uni_vocabulary_20.txt',
                                                  'vocabularies/text_to_vector_uni_vocabulary_-1.txt',
                                                  'vocabularies/text_to_vector_vocabulary.txt'],
                #'text_to_vector_bi_vocabulary': ['vocabularies/text_to_vector_bi_vocabulary.txt'],
                'tf_idf_vector': [True, False],
                'counter_vector': [True, False],
                #'binary_vector': [True,False],
                'best_representing_words_list': ['vocabularies/service_best_words.txt',
                                                 'vocabularies/service_best_words_10.txt',
                                                 'vocabularies/service_best_words_12.txt',
                                                 'vocabularies/service_best_words_custom.txt'],
                'surrounding_words': [True, False],
                'polarity_vocabulary': 'vocabularies/polarity_words.txt',
                'polarity_count': [True, False],
                'parts_of_speech': [True, False],
                'uni_gram': [True, False],
#                'bi_gram': [True, False],
                'not_count': [True, False],
                'remove_stop_words': [True, False]
            }
    classifiers = {
        'SVC_linear': SVC(kernel='linear'),
        'SVC_linear_C0,1': SVC(kernel='linear', C=0.1),
        'SVC_linear_C10': SVC(kernel='linear', C=10),
        'SVC_linear_C10_Gamma0,01': SVC(kernel='linear', C=10, gamma=0.01),
        'Decision_tree_maxdepth6': tree.DecisionTreeClassifier(max_depth=6),
        'Decision_tree': tree.DecisionTreeClassifier(),
        'GaussianNB': GaussianNB(),
        'Random_forest': RandomForestClassifier()
    }

    class_map = {0: 0,
                 1: 1,
                 # 2: 2,
                 3: 3}

    train_model.get_best_config(src_path=src_path,
                                data_field=data_field,
                                target_field=target_field,
                                feature_extraction_config=feature_extraction_config,
                                classifiers=classifiers,
                                class_map=class_map)


def train_model_for_debug():
    feature_extraction_config = {
        'text_to_vector_uni_vocabulary': 'vocabularies/text_to_vector_uni_vocabulary_10.txt',
        'text_to_vector_bi_vocabulary': 'vocabularies/text_to_vector_bi_vocabulary.txt',
        'tf_idf_vector': False,
        'counter_vector': True,
        'binary_vector': False,
        'best_representing_words_list': 'vocabularies/service_best_words_custom.txt',
        'surrounding_words': True,
        'polarity_vocabulary': 'vocabularies/polarity_words.txt',
        'positive_words_count': True,
        'negative_words_count': True,
        'polarity_count': True,
        'parts_of_speech': True,
        'uni_gram': True,
        'bi_gram': False,
        'not_count': False,
        'remove_stop_words': False
    }

    class_map = {0: 0,
                 1: 1,
                 # 2: 2,
                 3: 3}

    data, target, original_text = train_model.prepare_data(src_path=src_path,
                                            data_field=data_field,
                                            target_field=target_field,
                                            class_map=class_map,
                                            balance_classes=False,
                                            randomize=False,
                                            feature_config=feature_extraction_config)
    clf = SVC(kernel='linear')

    train_model.test_model(clf, data, target, original_text, 'service_quality_mistakes.csv', verbose=True)

def train():
    feature_extraction_config = {
        'text_to_vector_uni_vocabulary': 'vocabularies/text_to_vector_uni_vocabulary_10.txt',
        'text_to_vector_bi_vocabulary': 'vocabularies/text_to_vector_bi_vocabulary.txt',
        'tf_idf_vector': False,
        'counter_vector': True,
        'binary_vector': False,
        'best_representing_words_list': 'vocabularies/service_best_words_custom.txt',
        'surrounding_words': True,
        'polarity_vocabulary': 'vocabularies/polarity_words.txt',
        'positive_words_count': True,
        'negative_words_count': True,
        'polarity_count': True,
        'parts_of_speech': True,
        'uni_gram': True,
        'bi_gram': False,
        'not_count': False,
        'remove_stop_words': False
    }

    class_map = {0: 0,
                 1: 1,
                 # 2: 2,
                 3: 3}

    clf = SVC(kernel='linear')

    train_model.train_model(clf,
                            src_path=src_path,
                            data_field=data_field,
                            target_field=target_field,
                            export_path='Classifiers/Service_model.pkl',
                            class_map=class_map,
                            balance_classes=False,
                            randomize=False,
                            feature_config=feature_extraction_config)

#check_best_config()
#train_model_for_debug()
train()
