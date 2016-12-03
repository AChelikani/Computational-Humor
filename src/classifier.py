
from sklearn.multiclass import OneVsRestClassifier
from sklearn.svm import LinearSVC

import numpy as np

scores = []
y = []
f = open("scores.txt")
for line in f.readlines():
    homophones, references, classy, y_1 = line.split(",")
    scores.append([float(homophones), float(references), float(classy)])
    y.append([float(y_1)])

scores = np.array(scores)
y = np.array(y)

model = OneVsRestClassifier(LinearSVC(random_state=0)).fit(scores, y)

def predict(homophones, references, classy):
    X = np.array([[homophones, references, classy]])
    return model.predict(X)[0]
