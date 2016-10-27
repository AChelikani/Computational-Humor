import requests
import config
import words
import nltk

class Trainer(object):
    def __init__(self):
        self.entries = nltk.corpus.cmudict.entries()

    # Need word semantic similarity API for this
    def freqCounts(self):
        pass

    # Given an array of comments (as nested list), word synonyms from the tags
    # Gives all the funny words (i.e. comments - tags)
    def cleanComments(self, comments, syns):
        funny = []
        for x in range(len(comments)):
            comment = comments[x]
            tmp = []
            for y in range(len(comment)):
                word = comment[y]
                if word not in syns and word not in words.COMMON_WORDS:
                    tmp.append(word)
            funny.append(tmp)
        return funny

    # Given a set of words, returns a set of words + synonyms
    def populateSynonyms(self, arr):
        syns = set([])
        for word in arr:
            syns.add(word)
            resp = self.getSynonyms(word)
            for syn in resp:
                syns.add(syn)
        return syns

    # Gets a list of synonyms for a word
    def getSynonyms(self, word):
        url = "http://words.bighugelabs.com/api/2/" + config.WORD_AUTH + "/" + word + "/json"
        response = requests.get(url).json()
        for key in response:
            if (key == "noun"):
                return response[key]["syn"]
        return []

    def getSimilarity(self, word1, word2):
        url = "http://swoogle.umbc.edu/SimService/GetSimilarity?operation=api&phrase1=" + word1 + "&phrase2=" + word2
        response = requests.get(url).json()
        return response

    # Gets a list of rhyming words for a word
    def getRhymingWords(self, word):
        # Gets syllables of word.
        for entry, syllables in self.entries:
            if entry == word:
                break

        # Checks last syllable of all candidate words in dictionary.
        rhymes = [cand for cand, cand_syl in self.entries if syllables[-1] == cand_syl[-1]]
        return rhymes

    # Gets a list of rhyming synonyms for a word
    def getRhymingSynonyms(self, word):
        syns = set(self.getSynonyms(word))
        rhymes = set(self.getRhymingWords(word))

        return syns.intersection(rhymes)



if __name__ == "__main__":
    trainer = Trainer()
    #print trainer.getSimilarity("My delicious salad from a Domino's pizza in Sarasota (refund denied).", "salad")
    #print trainer.getSynonyms("help")
    print trainer.getRhymingSynonyms("waiter")
