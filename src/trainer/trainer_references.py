import os
import textwrap
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.externals import joblib
from trainer_metrics import *
from trainer_synonyms import *

def referencesScore(rep, word, tags):
    '''
    Add results of the following scoring functions:
        1) Relative edit distance between <word> and <rep>
        2) Edit distance between soundex codes <word> and <rep>
        3) Pronunciation similarity between <rep> and <word>
        4) Similarity of <rep> with <tags>
        5) Length of <rep>
    '''
    scores = []
    scores.append(editSimilarity(rep, word))
    scores.append(soundexDistance(rep, word))
    scores.append(pronunciationSimilarity(rep, word))
    scores.append(0)
    for tag in tags:
        scores[-1] += getSimilarity(rep, tag)
    scores.append(len(rep))
    return scores

def referencesData():
    '''
    Extracts data to train model for run_references().
    '''
    X = []
    Y = []

    for datafile in os.listdir("../examples/ref_outputs"):
        f = open("../examples/ref_outputs/" + datafile)
        while True:
            comment = f.readline()
            if comment == "DONE\n":
                break

            scores = f.readline()[1:-2].split(", ")
            x = [float(score) if score[-3:] != "inf" else -1. for score in scores]
            X.append(x)

            y = float(f.readline()[:-1])
            Y.append(y)

    data = train_test_split(X, Y)

    return data

def referencesTrain():
    '''
    Trains logistic regression model to be used by run_references() and
    saves it.
    '''
    X_train, X_test, Y_train, Y_test = referencesData()

    clf = LinearRegression()
    clf.fit(X_train, Y_train)

    results = open("references_model/log.txt", 'w')
    print >> results, "X_train"
    print >> results, X_train
    print >> results, "Y_train"
    print >> results, Y_train
    print >> results, "X_test"
    print >> results, X_test
    print >> results, "Y_test"
    print >> results, Y_test
    print >> results, "Score"
    print >> results, clf.score(X_test, Y_test)

    joblib.dump(clf, 'references_model/model.pkl') 
