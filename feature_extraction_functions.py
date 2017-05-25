import NLP_Utils

"""
    Gets text and vocabulary and transfoms it to vector
    with tf-idf
"""
def text_2_tf_idf_vector(text, vocabulary):
    hot_vector = [0] * len(vocabulary)
    word_counter = dict()
    words_not_in_vocabulary = 0

    for word in str(NLP_Utils.remove_non_letters(text)).split():
        word = NLP_Utils.stem_word(word)
        word_counter[word] = word_counter.get(word, 0) + 1

    for word, value in word_counter.iteritems():
        if vocabulary.has_key(word):
            hot_vector[vocabulary[word].get_index()] = float(word_counter[word]) / float(vocabulary[word].get_freq())
        else:
            words_not_in_vocabulary += 1

    return hot_vector

"""
    Gets text and vocabulary and transfoms it to vector
    with each cell counts number of repetitions of word
"""
def text_2_repetitions_vector(text, vocabulary):
    hot_vector = [0] * len(vocabulary)
    word_counter = dict()
    words_not_in_vocabulary = 0

    for word in str(NLP_Utils.remove_non_letters(text)).split():
        word = NLP_Utils.stem_word(word)
        word_counter[word] = word_counter.get(word, 0) + 1

    for word, value in word_counter.iteritems():
        if vocabulary.has_key(word):
            hot_vector[vocabulary[word].get_index()] = float(word_counter[word])
        else:
            words_not_in_vocabulary += 1

    return hot_vector


"""
    Gets text and vocabulary and transfoms it to vector
    each cell if word appeared
"""
def text_2_binary_vector(text, vocabulary):
    hot_vector = [0] * len(vocabulary)
    word_counter = dict()
    words_not_in_vocabulary = 0

    for word in str(NLP_Utils.remove_non_letters(text)).split():
        word = NLP_Utils.stem_word(word)
        word_counter[word] = word_counter.get(word, 0) + 1

    for word, value in word_counter.iteritems():
        if vocabulary.has_key(word):
            hot_vector[vocabulary[word].get_index()] = 1
        else:
            words_not_in_vocabulary += 1

    return hot_vector


def get_surrounding_words(text, core_words, words_before=3, words_after=7):
    reps = 0

    surrounding_words = []
    text = str(NLP_Utils.remove_non_letters(text)).split()

    for i,word in enumerate(text):
        word = NLP_Utils.stem_word(word)

        if word in core_words:
            reps += 1
            if i < words_before:
                start_index = 0
            else:
                start_index = i - words_before

            if i +words_after >= len(text):
                end_index = len(text)
            else:
                end_index = i + words_after

            surrounding_words.extend(text[start_index:end_index])

    return " ".join(surrounding_words), reps


def prepare_text(text, config):
    prepared_text = list()

    if config['surrounding_words']:
        text,reps = get_surrounding_words(text, config['best_representing_words_list'])
        prepared_text.extend([reps])
    if config['tf_idf_vector']:
        prepared_text.extend(text_2_tf_idf_vector(text, config['text_to_vector_vocabulary']))
    if config['counter_vector']:
        prepared_text.extend(text_2_repetitions_vector(text, config['text_to_vector_vocabulary']))
    if config['binary_vector']:
        prepared_text.extend(text_2_binary_vector(text, config['text_to_vector_vocabulary']))

    return prepared_text