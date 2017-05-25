import re
from stemming.porter2 import stem
import simplejson as json
from nltk.stem.porter import *

"""
initialize items once
"""
pattern1 = re.compile('[\W_]+')
pattern2 = re.compile('\'')
stemmer = PorterStemmer()

def remove_non_letters(str):
    return pattern1.sub(' ', pattern2.sub('', str))

def stem_word(word):
    return stemmer.stem(word)