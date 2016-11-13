import requests
from trainer_synonyms import getSynonymsList


def getRhyming(word):
    '''
    Finds a list of rhyming words for a word.
    '''
    rhymes = []
    url = "http://rhymebrain.com/talk?function=getRhymes&word=%s" % word
    response = requests.get(url).json()

    for word in response:
        score = int(word["score"])
        if (score == 300):
            rhymes.append(word["word"])

    return rhymes

def getRhymingSynonyms(word, level):
    '''
    Finds a set of rhyming synonyms for a word.
    '''
    syns = set(getSynonymsList(word, level))
    rhymes = set(getRhyming(word))
    return syns.intersection(rhymes)

def populateRhyme(words):
    '''
    Given a list or set of words, returns a set of rhyming words.
    '''
    res = []
    for word in words:
        res.extend(getRhyming(word))

    return set(res)
