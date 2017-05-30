import NLP_Utils
import re
import vocabularies

def prepare_text(text, config):
    #region load vocab
    if config.has_key('polarity_vocabulary'):
        if isinstance(config['polarity_vocabulary'], str):
            config['polarity_vocabulary'] = vocabularies.read_polarity_vocabulary(
                config['polarity_vocabulary'])
    if config.has_key('best_representing_words_list'):
        if isinstance(config['best_representing_words_list'], str):
            config['best_representing_words_list'] = vocabularies.read_best_words_list(
                config['best_representing_words_list'])
    if config.has_key('text_to_vector_bi_vocabulary'):
        if isinstance(config['text_to_vector_bi_vocabulary'], str):
            config['text_to_vector_bi_vocabulary'] = vocabularies.read_vocabulary(
                config['text_to_vector_bi_vocabulary'])
    if config.has_key('text_to_vector_uni_vocabulary'):
        if isinstance(config['text_to_vector_uni_vocabulary'], str):
            config['text_to_vector_uni_vocabulary'] = vocabularies.read_vocabulary(
                config['text_to_vector_uni_vocabulary'])
    #endregion
    prepared_text = list()

    if config.has_key('remove_stop_words'):
        if config['remove_stop_words']:
            text = remove_stopwords(text)

    if config.has_key('surrounding_words'):
        if config['surrounding_words']:
            text,reps = get_surrounding_words(text, config['best_representing_words_list'])
            prepared_text.extend([reps])

    positive_words_count = False
    negative_words_count = False
    polarity_count = False
    if config.has_key('polarity_count'):
        if config['polarity_count']:
            prepared_text.extend(count_polarity_words(text, config['polarity_vocabulary']))
    if config.has_key('parts_of_speech'):
        if config['parts_of_speech']:
            prepared_text.extend(calc_pos_rank(text))
    if config.has_key('not_count'):
        if config['not_count']:
            prepared_text.extend([not_counter(text)])

    if config.has_key('bi_gram'):
        if config['bi_gram']:
            if config.has_key('tf_idf_vector'):
                if config['tf_idf_vector']:
                    prepared_text.extend(text_2_tf_idf_bi_vector(text, config['text_to_vector_bi_vocabulary']))
            if config.has_key('counter_vector'):
                if config['counter_vector']:
                    prepared_text.extend(text_2_repetitions_bi_vector(text, config['text_to_vector_bi_vocabulary']))
            if config.has_key('binary_vector'):
                if config['binary_vector']:
                    prepared_text.extend(text_2_binary_bi_vector(text, config['text_to_vector_bi_vocabulary']))
    if config.has_key('uni_gram'):
        if config['uni_gram']:
            if config.has_key('tf_idf_vector'):
                if config['tf_idf_vector']:
                    prepared_text.extend(text_2_tf_idf_vector(text, config['text_to_vector_uni_vocabulary']))
            if config.has_key('counter_vector'):
                if config['counter_vector']:
                    prepared_text.extend(text_2_repetitions_vector(text, config['text_to_vector_uni_vocabulary']))
            if config.has_key('binary_vector'):
                if config['binary_vector']:
                    prepared_text.extend(text_2_binary_vector(text, config['text_to_vector_uni_vocabulary']))

    return prepared_text
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


def count_polarity_words(text, vocabulary):
    positive = 0
    negative = 0

    text = text.split()

    for word in text:
        word = NLP_Utils.stem_word(word)

        if word in vocabulary:
            if vocabulary[word] == 1:
                positive += 1
            else:
                negative += 1

    return positive, negative, positive - negative


def calc_pos_rank(text):
    nouns_count = 0
    adjectives_count = 0
    verbs_count = 0
    pos_tags = NLP_Utils.text_2_part_of_speech_tag(text)

    for word_token in pos_tags:
        if word_token[1][:2] == 'NN':
            nouns_count += 1
        elif word_token[1][:2] == 'JJ':
            adjectives_count += 1
        elif word_token[1][:2] == 'VB':
            adjectives_count += 1

    return adjectives_count, nouns_count, verbs_count




"""
    Gets text and vocabulary and transfoms it to vector
    with tf-idf
"""
def text_2_tf_idf_bi_vector(text, vocabulary):
    hot_vector = [0] * len(vocabulary)
    word_counter = dict()
    words_not_in_vocabulary = 0
    prev_word = None

    for word in str(NLP_Utils.remove_non_letters(text)).split():
        word = NLP_Utils.stem_word(word)

        if prev_word is not None:
            word_counter[prev_word + '-' + word] = word_counter.get(prev_word + '-' + word, 0) + 1

        prev_word = word

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
def text_2_repetitions_bi_vector(text, vocabulary):
    hot_vector = [0] * len(vocabulary)
    word_counter = dict()
    words_not_in_vocabulary = 0
    prev_word = None

    for word in str(NLP_Utils.remove_non_letters(text)).split():
        word = NLP_Utils.stem_word(word)

        if prev_word is not None:
            word_counter[prev_word + '-' + word] = word_counter.get(prev_word + '-' + word, 0) + 1

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
def text_2_binary_bi_vector(text, vocabulary):
    hot_vector = [0] * len(vocabulary)
    word_counter = dict()
    words_not_in_vocabulary = 0
    prev_word = None

    for word in str(NLP_Utils.remove_non_letters(text)).split():
        word = NLP_Utils.stem_word(word)
        if prev_word is not None:
            word_counter[prev_word + '-' + word] = word_counter.get(prev_word + '-' + word, 0) + 1

    for word, value in word_counter.iteritems():
        if vocabulary.has_key(word):
            hot_vector[vocabulary[word].get_index()] = 1
        else:
            words_not_in_vocabulary += 1

    return hot_vector


def not_counter(text):
    return len(re.findall(r"not", text.lower()))


def remove_stopwords(text):
    text = text.split()

    for i,word in enumerate(text):
        word = NLP_Utils.stem_word(word)
        if NLP_Utils.is_word_stop_word(word):
            text[i] = word

    return ' '.join(text)