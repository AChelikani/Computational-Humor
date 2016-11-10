import requests
import config
import words
import nltk
import clarifai
import reddit
import re
from insultingwords import INSULTING_WORDS

class Trainer(object):
    def __init__(self):
        #self.entries = nltk.corpus.cmudict.entries()
        self.clarifai = clarifai.Clarifai(config.CLARIFAI_AUTH)
        self.reddit = reddit.Reddit("Computation Humor 1.0")
        self.reddit.connect()



    # Populates funny words, i.e. comments - tags, using cleanComments
    def populateFunny(self, comments, syns):
        return set(self.cleanComments(comments, syns))

    # Given an array of comments (as a nested list) and synonyms from the tags
    # Gives all the funny words (i.e. comments - tags) as a single unnested list
    def cleanComments(self, comments, syns):
        regex = re.compile('[^a-zA-Z\s\']')
        funny = []
        for x in range(len(comments)):
            comment = comments[x].lower()
            comment = regex.sub('', comment)
            comment = comment.split(" ")
            tmp = []
            for y in range(len(comment)):
                word = comment[y]
                if word not in syns and word not in words.COMMON_WORDS:
                    tmp.append(word)
            funny.extend(tmp)
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
        try:
            response = requests.get(url).json()
            for key in response:
                if (key == "noun"):
                    return response[key]["syn"]
        except:
            return []
        return []

    # Gets a list of synonyms until a certain depth
    def getSynonymsList(self, word, level):
        allSynonyms = [word]
        curSynonyms = [word]
        nextWords = []
        for i in range(0, level):
            for w in curSynonyms:
                synonyms = self.getSynonyms(w)
                allSynonyms.extend(synonyms)
                nextWords.extend(synonyms)
            curSynonyms = nextWords
            nextWords = []
        return allSynonyms

    # Calculates the similarity between two words
    def getSimilarity(self, word1, word2):
        url = "http://swoogle.umbc.edu/SimService/GetSimilarity?operation=api&phrase1=" + word1 + "&phrase2=" + word2
        response = requests.get(url).json()
        return response



    # Given a set of words, returns a set of rhyming words
    def populateRhyming(self, arr):
        res = []
        for word in arr:
            res.extend(self.getRhyming(word))
        return set(res)

    # Get rhyming words
    def getRhyming(self, word):
        rhymes = []
        response = requests.get("http://rhymebrain.com/talk?function=getRhymes&word=" + word).json()
        for word in response:
            score = int(word["score"])
            if (score == 300):
                rhymes.append(word["word"])
        return rhymes

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
    def getRhymingSynonyms(self, word, level):
        syns = set(self.getSynonymsList(word, level))
        rhymes = set(self.getRhyming(word))
        return list(syns.intersection(rhymes))



    ### Main run functions

    # Funny intersects with rhyming
    def run1(self, postID):
        comments, imgUrl, votes = self.reddit.getCommentsById(postID)

        tags = self.clarifai.makeRequest(imgUrl)
        synTags = self.populateSynonyms(tags)
        funny = self.cleanComments(comments, synTags)

        for word in funny:
            tmp = self.getRhyming(word)
            for rhymingWord in tmp:
                if rhymingWord in synTags:
                    print word, rhymingWord
        return funny

    # Rhyming of synonyms of funny intersects with synonyms of tags
    def run2(self, postID):
        comments, imgUrl, votes = self.reddit.getCommentsById(postID)

        tags = self.clarifai.makeRequest(imgUrl)
        synTags = self.populateSynonyms(tags)
        funny = self.populateFunny(comments, synTags)
        insulting = set(INSULTING_WORDS)
        funny.union(insulting)
        synFunny = self.populateSynonyms(funny)
        print "##############################"
        print synFunny

        rhymeSynFunny = self.populateRhyming(synFunny)
        result = rhymeSynFunny.intersection(synTags)
        print "##############################"
        print rhymeSynFunny
        print "##############################"
        print result

        return synFunny, result



if __name__ == "__main__":
    trainer = Trainer()
    trainer.run2("5a60vf")
