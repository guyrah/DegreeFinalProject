import vocabularies

data_path = 'tagged_data.json'
data_field = 'text'
target_field = 'quality_of_service_rank'
#target_field = 'clean_rank'
target_field = 'big_dish_rank'
# target_field = 'value_for_money_rank'
vocabulary_path = 'text_to_vector_vocabulary.txt'
from sklearn.svm import SVC
text_to_vector_vocabulary = vocabularies.read_vocabulary('vocabularies/text_to_vector_vocabulary.txt')

feature_extraction_config = {
    'tf_idf_vector': False,
    'counter_vector': True,
    'binary_vector': False,
    'text_to_vector_uni_vocabulary': text_to_vector_vocabulary,
    'uni_gram': True,
}

#vocabularies.create_words_polarity_vocabulary('positive-words_raw.txt', 'negative-words_raw.txt', 'polarity_words_vocabulary.txt')
#a = vocabularies.read_polarity_vocabulary('polarity_words_vocabulary.txt')
#vocabularies.create_best_words_list(data_path=data_path, data_field=data_field, target_field=target_field, save_path='clean_best_words.txt', number_of_words=10, config=feature_extraction_config)
#vocabularies.create_bi_vocabulary(data_path, 'text_to_vector_bi_vocabulary.txt', 2)
#vocabularies.create_vocabulary(data_path, 'text_to_vector_uni_vocabulary_10.txt', 10)
vocabularies.create_best_words_list(data_path=data_path, data_field=data_field, target_field=target_field, save_path='vocabularies/dish_size_best_words_10.txt', number_of_words=10, config=feature_extraction_config)