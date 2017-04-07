import re
from stemming.porter2 import stem
from nltk.stem.porter import *

class WordManipulator:
    pattern1 = re.compile('[\W_]+')
    pattern2 = re.compile('\'')
    stemmer = PorterStemmer()

    def remove_non_letters(self, str):
        return self.pattern1.sub(' ', self.pattern2.sub('', str))

    def stem_word(self,word):
        return self.stemmer.stem(word)


