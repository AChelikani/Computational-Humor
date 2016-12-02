# Prevents .pyc files from being written
import sys
sys.dont_write_bytecode = True

import re
import config
from sklearn.externals import joblib
import words
from wrappers import clarifai, reddit
from trainer import populateFunny, populateSynonyms, populateRhyme, \
                    getSimilarity, getHomophones, editDistance, \
                    soundexDistance, pronunciationSimilarity, wordEquality, \
                    referencesScore


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
        # self.getClassyImage = getClassyImage
        # self.getClassyPhrase = getClassyPhrase

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
        # return sorted(res, reverse=True)

    def run_references(self, postID, print_output=False):
        '''
        Replaces words with references.
        '''
        comments, imgUrl, votes = self.reddit.getCommentsById(postID)
        tags = self.clarifai.makeRequest(imgUrl)
        synTags = self.populateSynonyms(tags) - words.COMMON_WORDS

        synTagsLower = [tag.lower() for tag in synTags]
        referencesSplit = [reference.split() for reference in words.REFERENCE_WORDS]

        comments = []
        for rep in synTagsLower:
            for ref in referencesSplit:
                # For each reference, check whether <rep> can replace a word in
                # the reference.
                for i, word_mod in enumerate(ref):
                    # Adds capitalization and punctuation.
                    word = word_mod.lower()

                    rep_mod = rep.title() if word_mod.istitle() else rep
                    if not word_mod[-1].isalpha():
                        rep_mod += word_mod[-1]
                        word = word[:-1]

                    # Check that word and rep are not the same and that word
                    # is not a common word, and they are close by some metric.
                    # Note that these parameters were found by experimentation.
                    if word not in words.COMMON_WORDS and not wordEquality(rep, word) \
                    and (editDistance(rep, word) == 1 or soundexDistance(rep, word) == 0):
                        ref_copy = ref[:]
                        ref_copy[i] = rep_mod
                        phrase = ' '.join(ref_copy)

                        scores = referencesScore(rep, word, tags)
                        if print_output:
                            print phrase
                            print scores
                            print

                        comments.append([phrase, scores])

        if print_output:
            print "DONE"

        clf = joblib.load("trainer/references_model/model.pkl")
        for comment in comments:
            comment.extend(clf.predict([comment[1]]))

        comments.sort(key=lambda comment: comment[2])
        return comments[0][0], comments[0][2]



    '''
    def run_classy(self, postID):
        comments, imgUrl, votes = self.reddit.getCommentsById(postID)

        tags = self.clarifai.makeRequest(imgUrl)
        synTags = self.populateSynonyms(tags) - words.COMMON_WORDS
        classy = self.getClassyImage(synTags)
        print classy
        return self.getClassyPhrase(classy)
    '''


if __name__ == "__main__":
    trainer = Trainer()
    #print trainer.run_synRhyme("4aozus")
    #print trainer.run_synRhyme("4qxqnq")

    # f_ref = open("examples/ref_examples.txt")
    # for line in f_ref:
    #     if line[0] == "#":
    #         continue
    #     f_output = open("examples/ref_outputs/%s" % line[:-1], 'w')
    #     sys.stdout = f_output
    #     trainer.run_references(line)
    #     f_output.close()
    # f_ref.close()
    print trainer.run_references("4qxqnq")

    '''
    f = open("examples/calibration.txt")
    for line in f.readlines():
        print "\n" + line
        print "Homophones"
        print trainer.run_homophones(line)
        print "\nReferences"
        print trainer.run_references(line)
        print "\nClassy"
        print trainer.run_classy(line)
    '''


    # res = trainer.run_classy("1h7o7f")
    # print res
    # print "-----ordered------"
    # for item in res:
    #     print item
