import textwrap
from trainer_metrics import *
from trainer_synonyms import *

def referencesScore(rep, word, tags):
    '''
    Add results of the following scoring functions:
      1) Edit distance between <word> and <rep> of spelling
      2) Edit distance between <word> and <rep> of soundex
      3) Similarity of <rep> with all words in <tags>
      4) Length of <rep>
      5) Pronunciation similarity between <rep> and <word>
    '''
    scores = []
    scores.append(editDistance(rep, word))
    scores.append(soundexDistance(rep, word))
    scores.append(0)
    for tag in tags:
        scores[-1] += getSimilarity(rep, tag)
    scores.append(len(rep))
    scores.append(pronunciationSimilarity(rep, word))
    return scores

def referencesPrint(phrase, scores):
    '''
    Print generated phrase and list of scores.
    '''
    phrase_text = textwrap.wrap(phrase, 40)

    for i, text in enumerate(phrase_text):
        if i != len(phrase_text) - 1:
            print text
    print ("%-45s" % text),

    scores_text = "["
    for score in scores:
        # Jank but whatever
        if score < 10:
            scores_text += "%4.2f, " % score
        else:
            scores_text += "%4.1g, " % score
    scores_text = scores_text[:-2]
    scores_text += "]"
    print scores_text
