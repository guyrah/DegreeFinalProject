import re
from stemming.porter2 import stem
import simplejson as json
from nltk.stem.porter import *
from nltk import pos_tag
from nltk import word_tokenize

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

def text_2_part_of_speech_tag(text):
    return pos_tag(word_tokenize(text))

