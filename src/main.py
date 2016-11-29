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

        res = []

        for word in tags:
            hphones = self.getHomophones(word)
            for homophone in hphones:
                for title_word in title:
                    hphone, hscore = homophone
                    score = self.getSimilarity(hphone, title_word) + hscore/17800.0
                    if (score > 0):
                        #print "%s %s \t score: %f, %f" % (hphone, title_word, score, hscore)
                        res.append((score, hphone + " " + title_word))

        for word in title:
            hphones = self.getHomophones(word)
            for homophone in hphones:
                for title_word in tags:
                    hphone, hscore = homophone
                    score = self.getSimilarity(hphone, title_word) + hscore/17800.0
                    if (score > 0):
                        #print "%s %s \t score: %f, %f" % (hphone, title_word, score, hscore)
                        res.append((score, hphone + " " + title_word))

        return sorted(res, reverse=True)[0][1]

    def run_references(self, postID, metric="edit", param=2):
        '''
        Replaces words with references.
        '''
        comments, imgUrl, votes = self.reddit.getCommentsById(postID)

        tags = self.clarifai.makeRequest(imgUrl)
        synTags = self.populateSynonyms(tags)

        for tag in synTags:
            for phrase in words.REFERENCE_WORDS:
                reference = phrase.split()
                tag = tag.lower()

                if tag not in words.COMMON_WORDS:
                    # For each reference, check whether a tag can replace a
                    # word in the reference.
                    for i in range(len(reference)):
                        word = reference[i]
                        tag_mod = tag

                        # Check that the word and the tag are not the same,
                        # and that the word is not a common word.
                        if word not in words.COMMON_WORDS and tag_mod != word.lower():
                            # Capitalizes tag.
                            if word.istitle():
                                tag_mod = tag_mod.title()
                            # Adds punctuation.
                            if not word[-1].isalpha():
                                tag_mod += word[-1]

                            # Use a metric as a measure of "closeness" to
                            # replace a word in a reference.

                            # Edit distance
                            if metric == "edit" and editDistance(tag_mod, word) <= param:
                                reference[i] = tag_mod
                                print "\t%s" % ' '.join(reference)
                                reference[i] = word
                            # Soundex distance
                            elif metric == "soundex" and soundexDistance(tag_mod, word) <= param:
                                reference[i] = tag_mod
                                print "\t%s" % ' '.join(reference)
                                reference[i] = word


if __name__ == "__main__":
    trainer = Trainer()
    #print trainer.run_synRhyme("4aozus")
    #print trainer.run_synRhyme("4qxqnq")

    # Optimal parameters found by experimentation
    for m, p in [("edit", 1), ("soundex", 0)]:
        print "Metric: %s-%d" % (m, p)
        trainer.run_references("5f7g0l", metric=m, param=p)
        print

    #res = trainer.run_homophones("5f62i1")
    #res = trainer.run_homophones("5f7g0l")
    #print res
    # print "-----ordered------"
    # for item in res:
    #     print item
