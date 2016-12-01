# Prevents .pyc files from being written
import sys
sys.dont_write_bytecode = True

import re
import config
import words
from wrappers import clarifai, reddit
from trainer import populateFunny, populateSynonyms, populateRhyme, \
                    getSimilarity, getHomophones, editDistance, \
                    soundexDistance, pronunciationSimilarity, \
                    referencesScore, referencesPrint


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
        self.getClassyImage = getClassyImage
        self.getClassyPhrase = getClassyPhrase

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

    def run_references(self, postID):
        '''
        Replaces words with references.
        '''
        comments, imgUrl, votes = self.reddit.getCommentsById(postID)
        tags = self.clarifai.makeRequest(imgUrl)
        synTags = self.populateSynonyms(tags) - words.COMMON_WORDS

        phrases = []
        for rep in [tag.lower() for tag in synTags]:
            for ref in [reference.split() for reference in words.REFERENCE_WORDS]:
                # For each reference, check whether rep can replace a word in
                # the reference.
                for i, word in enumerate(ref):
                    # Adds capitalization and punctuation.
                    rep_mod = rep.title() if word.istitle() else rep
                    word_bare = word.lower()
                    if not word[-1].isalpha():
                        rep_mod += word[-1]
                        word_bare = word_bare[:-1]

                    # Check that word and rep are not the same and that word
                    # is not a common word, and they are close by some metric.
                    # Note that these parameters were found by experimentation.
                    if word not in words.COMMON_WORDS and rep_mod != word \
                    and (editDistance(rep, word_bare) == 1
                    or soundexDistance(rep, word_bare) == 0):
                        ref_copy = ref[:]
                        ref_copy[i] = rep_mod
                        phrase = ' '.join(ref_copy)

                        scores = referencesScore(rep, word, tags)
                        referencesPrint(phrase, scores)

                        phrases.append((phrase, scores))


        ### TODO: list of responses and scores as output
        ### Outputs an empty list at most 50% of the time
        ### Friday: go through 100 images, choose best phrases from the
        ### three algorithms and score them for each image
        ### Normalize each scoring function to be on same range and
        ### distribution

        ### BOT: given a picture, runs it through each scoring function
        ### and normalizes; if the score is higher than a threshold then
        ### comment

    def run_classy(self, postID):
        comments, imgUrl, votes = self.reddit.getCommentsById(postID)

        tags = self.clarifai.makeRequest(imgUrl)
        synTags = self.populateSynonyms(tags) - words.COMMON_WORDS
        classy = self.getClassyImage(synTags)
        print classy
        return self.getClassyPhrase(classy)


if __name__ == "__main__":
    trainer = Trainer()
    #print trainer.run_synRhyme("4aozus")
    #print trainer.run_synRhyme("4qxqnq")

    # Optimal parameters found by experimentation
    ### TODO: Based on many images come up with ~5 quantities that may
    ### matter, score phrases, and then do regression
    ###
    ### e.g. for each example we generate we get average similarity between
    ### phrase and tags, similarity on how they look, how they are
    ### pronounced, etc. and manually give each phrase a score.
    ### Run logistic regression.
    ### If not enough samples then instead of regression just do
    ### heuristic.
    trainer.run_references("5f7g0l")
    # trainer.run_references("4aozus")
    # trainer.run_references("4qxqnq")
    # trainer.run_references("5f62i1")
    # trainer.run_references("5f7g0l")
    # trainer.run_references("5fbr5s")
    # trainer.run_references("5fbigs")
    # trainer.run_references("5fdi09")
    print

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
