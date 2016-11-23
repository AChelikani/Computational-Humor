import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from words.classy_words import CLASSY_WORDS
from trainer_word2vec import Word

import numpy as np
from sklearn.decomposition import PCA

x = None

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
