# Prevents .pyc files from being written
import sys
sys.dont_write_bytecode = True

import re
import config
import words
from wrappers import clarifai, reddit
from trainer import populateFunny, populateSynonyms, populateRhyme, getSimilarity, \
                    getHomophones, editDistance, soundexDistance


class Trainer(object):
    '''
    Main trainer class that outputs a comment given a post.
    '''

    def __init__(self):
        self.populateFunny = populateFunny
        self.populateSynonyms = populateSynonyms
        self.populateRhyme = populateRhyme
        self.getSimilarity = getSimilarity
        self.getHomophones = getHomophones

        self.clarifai = clarifai.Clarifai(config.CLARIFAI_AUTH)
        self.reddit = reddit.Reddit("Computation Humor 1.0")
        self.reddit.connect()


    def run_synRhyme(self, postID):
        '''
        Pairs a (synonym of a) funny word with a word that rhymes with it and
        is a synonym of a tag.
        '''
        comments, imgUrl, votes = self.reddit.getCommentsById(postID)

        tags = self.clarifai.makeRequest(imgUrl)
        synTags = self.populateSynonyms(tags)
        funny = self.populateFunny(comments, synTags).union(words.INSULTING_WORDS)
        synFunny = self.populateSynonyms(funny, syn=True)

        best_score = 0

        for funnyWord in synFunny:
            rhymeSynFunny = self.populateRhyme([funnyWord])
            result = rhymeSynFunny.intersection(synTags)

            for resultWord in result:
                score = 0
                for tag in tags:
                    tagScore = self.getSimilarity(tag, funnyWord) \
                               + self.getSimilarity(tag, resultWord)

                    # Avoids -inf errors.
                    if tagScore > 0:
                        score += tagScore

                print "%s %s \tscore: %f" % (funnyWord, resultWord, score)

                if score > best_score:
                    best_phrase = (funnyWord, resultWord)
                    best_score = score

        return "What is this, %s %s?" % best_phrase

    def run_homophones(self, postID):
        comments, imgUrl, votes = self.reddit.getCommentsById(postID)
        title = self.reddit.getPostTitleById(postID)

        tags = self.clarifai.makeRequest(imgUrl)
        print "Tags: done \n"
        regex = re.compile('[^a-zA-Z\s\']')
        title = title.lower()
        title = regex.sub('', title)
        title = title.split(" ")
        print "Title: done \n"


        for word in tags:
            hphones = self.getHomophones(word)
            for homophone in hphones:
                for title_word in title:
                    hphone, hscore = homophone
                    score = self.getSimilarity(hphone, title_word)
                    if (score > 0):
                        print "%s %s \t score: %f" % (hphone, title_word, score)

        for word in title:
            hphones = self.getHomophones(word)
            for homophone in hphones:
                for title_word in tags:
                    hphone, hscore = homophone
                    score = self.getSimilarity(hphone, title_word)
                    if (score > 0):
                        print "%s %s \t score: %f" % (hphone, title_word, score)

    def run_references(self, postID):
        '''
        Replaces words with references.
        '''
        comments, imgUrl, votes = self.reddit.getCommentsById(postID)
    
        tags = self.clarifai.makeRequest(imgUrl)
        synTags = self.populateSynonyms(tags)

        for tag in synTags:
            for phrase in words.REFERENCE_WORDS:
                for word in phrase.split():
                    ### TODO: smaller numbers / use as parameters
                    if editDistance(tag, word) <= 5:
                        print "E\ttag, word"
                    elif soundexDistance(tag, word) <= 2:
                        print "S\ttag, word"

        # funny = self.populateFunny(comments, synTags).union(words.INSULTING_WORDS)
        # synFunny = self.populateSynonyms(funny, syn=True)

        # best_score = 0

        # for funnyWord in synFunny:
        #     rhymeSynFunny = self.populateRhyme([funnyWord])
        #     result = rhymeSynFunny.intersection(synTags)

        #     for resultWord in result:
        #         score = 0
        #         for tag in tags:
        #             tagScore = self.getSimilarity(tag, funnyWord) \
        #                        + self.getSimilarity(tag, resultWord)

        #             # Avoids -inf errors.
        #             if tagScore > 0:
        #                 score += tagScore

        #         print "%s %s \tscore: %f" % (funnyWord, resultWord, score)

        #         if score > best_score:
        #             best_phrase = (funnyWord, resultWord)
        #             best_score = score

        # return "What is this, %s %s?" % best_phrase

if __name__ == "__main__":
    trainer = Trainer()
    #print trainer.run_synRhyme("4aozus")
    #print trainer.run_synRhyme("4qxqnq")
    print trainer.run_references("4qxqnq")
