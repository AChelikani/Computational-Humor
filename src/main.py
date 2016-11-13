# Prevents .pyc files from being written
import sys
sys.dont_write_bytecode = True

import config
import words
from wrappers import clarifai, reddit


class Trainer(object):
    '''
    Main trainer class that outputs a comment given a post.
    '''

    def __init__(self):
        from trainer import populateFunny, populateSynonyms, populateRhyme
        self.populateFunny = populateFunny
        self.populateSynonyms = populateSynonyms
        self.populateRhyme = populateRhyme

        self.clarifai = clarifai.Clarifai(config.CLARIFAI_AUTH)
        self.reddit = reddit.Reddit("Computation Humor 1.0")
        self.reddit.connect()

    ### Main run functions

    # # Funny intersects with rhyming
    # def run1(self, postID):
    #     comments, imgUrl, votes = self.reddit.getCommentsById(postID)

    #     tags = self.clarifai.makeRequest(imgUrl)
    #     synTags = self.populateSynonyms(tags)
    #     funny = self.cleanComments(comments, synTags)

    #     for word in funny:
    #         tmp = self.getRhyming(word)
    #         for rhymingWord in tmp:
    #             if rhymingWord in synTags:
    #                 print word, rhymingWord
    #     return funny

    # Rhyming of synonyms of funny intersects with synonyms of tags
    # What is this, ___?
    def run2(self, postID):
        comments, imgUrl, votes = self.reddit.getCommentsById(postID)

        tags = self.clarifai.makeRequest(imgUrl)
        synTags = self.populateSynonyms(tags)
        funny = self.populateFunny(comments, synTags)
        funny = funny.union(words.INSULTING_WORDS)
        # synFunny = self.populateSynonyms(funny)
        synFunny = words.INSULTING_WORDS
        print tags
        print "##############################"
        print funny
        print "##############################"
        print synFunny
        print "##############################"

        # rhymeSynFunny = self.populateRhyming(synFunny)
        # result = rhymeSynFunny.intersection(synTags)
        # print "##############################"
        # print rhymeSynFunny
        # print "##############################"
        # print result

        # return synFunny, result

        best_phrase = ""
        best_score = 0

        for funnyWord in synFunny:
            rhymeSynFunny = self.populateRhyme([funnyWord])
            result = rhymeSynFunny.intersection(synTags)

            for resultWord in result:
                score = 0
                for tag in tags:
                    # score += self.getSimilarity(funnyWord, resultWord) \
                    #          * self.getSimilarity(tag, funnyWord)
                    tagScore = self.getSimilarity(tag, funnyWord) \
                               + self.getSimilarity(tag, resultWord)
                    if tagScore > 0:
                        score += tagScore

                print funnyWord, resultWord
                print score

                if score > best_score:
                    best_phrase = "%s %s" % (funnyWord, resultWord)
                    best_score = score

        return best_phrase

    # Rhyming of synonyms of funny intersects with synonyms of tags
    def run3(self, postID):
        comments, imgUrl, votes = self.reddit.getCommentsById(postID)

        tags = self.clarifai.makeRequest(imgUrl)
        synTags = self.populateSynonyms(tags)

        for syn in synTags:
            rhymeSynTags = self.populateRhyme([syn])
            result = rhymeSynTags.intersection(synTags)

            for resultWord in result:
                print syn, resultWord
                print self.getSimilarity(syn, resultWord)



if __name__ == "__main__":
    trainer = Trainer()
    trainer.run2("4aozus")
