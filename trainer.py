import requests
import config
import words
import nltk
import clarifai
import reddit
import re

class Trainer(object):
    def __init__(self):
        #self.entries = nltk.corpus.cmudict.entries()
        self.clarifai = clarifai.Clarifai(config.CLARIFAI_AUTH)
        self.reddit = reddit.Reddit("Computation Humor 1.0")
        self.reddit.connect()

    # Given an array of comments (as nested list), word synonyms from the tags
    # Gives all the funny words (i.e. comments - tags)
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
            funny.append(tmp)
        return funny

    def flattenComments(self, cleaned):
        res = []
        for comment in cleaned:
            res.extend(comment)
        return set(res)


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

    # Get rhyming words
    def getRhyming(self, word):
        rhymes = []
        response = requests.get("http://rhymebrain.com/talk?function=getRhymes&word=" + word).json()
        for word in response:
            score = int(word["score"])
            if (score == 300):
                rhymes.append(word["word"])
        return rhymes

    def populateRhyming(self, arr):
        res = []
        for word in arr:
            res.extend(self.getRhyming(word))
        return res

    # Gets a list of rhyming synonyms for a word
    def getRhymingSynonyms(self, word, level):
        syns = set(self.getSynonymsList(word, level))
        rhymes = set(self.getRhyming(word))
        return list(syns.intersection(rhymes))

    def getIntersection(self, set1, set2):
        return list(set1.intersection(set2))

    # Main method
    def run(self, postID):
        comments, imgUrl, votes = self.reddit.getCommentsById(postID)
        tags = self.clarifai.makeRequest(imgUrl)
        print tags
        print "####################"
        synTags = self.populateSynonyms(tags)
        print synTags
        print "####################"
        cleaned = self.flattenComments(self.cleanComments(comments, synTags))
        print cleaned
        print "####################"
        synFunny = cleaned
        print synFunny
        print "####################"
        for word in synFunny:
            tmp = self.getRhyming(word)
            for rhymingWord in tmp:
                if rhymingWord in synTags:
                    print word, rhymingWord
        return synFunny



if __name__ == "__main__":
    trainer = Trainer()
    trainer.run("5ao9jw")
    #print trainer.getRhyming("")
