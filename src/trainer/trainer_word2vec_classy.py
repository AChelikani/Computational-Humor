import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from words.classy_words import CLASSY_WORDS
from words.classy_phrases import CLASSY_PHRASES, NONCLASSY_PHRASES
from trainer_word2vec import Word

import numpy as np
import random
from sklearn.decomposition import PCA

x = None
classy_average = -20.24029400285

for word in CLASSY_WORDS:
    try:
        w = Word(word)
        if x is None:
            x = w.vec.reshape(w.vec.shape[0], 1)
        else:
            x = np.hstack((x, w.vec.reshape(w.vec.shape[0], 1)))
    except:
        pass


pca = PCA(n_components = 1)

v = pca.fit_transform(x).transpose()


def getClassy(w):
    return np.dot(v, w.vec.reshape(w.vec.shape[0], 1))[0][0]

def getClassyImage(tags):
    sum = 0
    n = 0
    for tag in tags:
        try:
            w = Word(tag)
            sum += getClassy(w)
            n += 1
        except:
            pass
    return float(sum) / n

def getClassyPhrase(classy):
    if classy < classy_average:
        return random.sample(CLASSY_PHRASES, 1)[0]
    else:
        return random.sample(NONCLASSY_PHRASES, 1)[0]
