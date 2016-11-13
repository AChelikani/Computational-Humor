import requests
import config


def getSynonyms(word):
    '''
    Finds a list of synonyms for a word.
    '''
    url = "http://words.bighugelabs.com/api/2/%s/%s/json" % (config.WORD_AUTH, word)

    try:
        response = requests.get(url).json()
        for key in response:
            if (key == "noun"):
                return response[key]["syn"]
    except Exception:
        pass

    return []

def getSynonymsList(word, level):
    '''
    Recursively finds a list of synonyms for a word until specified depth.
    '''
    allSynonyms = [word]
    curSynonyms = [word]
    nextWords = []

    for i in range(level):
        for syn in curSynonyms:
            synonyms = getSynonyms(syn)
            allSynonyms.extend(synonyms)
            nextWords.extend(synonyms)
        curSynonyms = nextWords
        nextWords = []

    return allSynonyms

def populateSynonyms(words):
    '''
    Given a list or set of words, returns a set of the words and their synonyms.
    '''
    syns = set([])
    for word in words:
        syns.add(word)
        resp = getSynonyms(word)
        syns = syns.union(resp)

    return syns

def getSimilarity(word1, word2):
    '''
    Calculates the similarity between two words.
    '''
    url = "http://swoogle.umbc.edu/SimService/GetSimilarity?operation=api&phrase1=%s&phrase2=%s" % (word1, word2)
    response = requests.get(url).json()
    return response
