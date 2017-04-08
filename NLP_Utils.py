import re
from stemming.porter2 import stem
from nltk.stem.porter import *

"""
Class which enables text preparations
"""
class WordManipulator:
    pattern1 = re.compile('[\W_]+')
    pattern2 = re.compile('\'')
    stemmer = PorterStemmer()

    def remove_non_letters(self, str):
        return self.pattern1.sub(' ', self.pattern2.sub('', str))

    def stem_word(self,word):
        return self.stemmer.stem(word)

"""
A vocabulray item containing
1. index for hot vector
2. freq in all training samples
"""
class VocabulrayItem:
    def __init__(self, index, frequency):
        self.index = index
        self.freq = frequency

    def get_index(self):
        return self.index

    def get_freq(self):
        return self.freq

"""
Gets path of vocabulary file and returns a vocabulary item
"""
def read_vocabulary(path):
    vocabulary = dict()

    with open(path, 'r') as file:
        for i, line in enumerate(file):
            line = line.split(',')
            vocabulary[str(line[0])] = VocabulrayItem(index=i, frequency=line[1])

    return vocabulary


def text_to_hot_vector(text, vocabulary):
    # TODO:
    return 1