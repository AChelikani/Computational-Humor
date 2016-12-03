from wrappers import reddit
import main
import classifier
import sys
import config

class RedditBot(object):
    def __init__(self):
        self.model = main.Trainer()

    def initializeBot(self, username, password):
        self.model.reddit.login(username, password)

    def makeComment(self, postID):
        # Compute scores and phrases of three methods
        homophoneScore, homophone = self.model.run_homophones(postID)
        reference, referenceScore = self.model.run_references(postID)
        classy, classyScore = self.model.run_classy(postID)
        bestChoice = classifier.predict(homophoneScore, referenceScore, classyScore)
        if (bestChoice == 0):
            self.model.reddit.postComment(homophone, postID)
            print "Commented: %s" % (homophone)
        elif (bestChoice == 1):
            self.model.reddit.postComment(reference, postID)
            print "Commented: %s" % (reference)
        elif (bestChoice == 2):
            self.model.reddit.postComment(classy, postID)
            print "Commented: %s" % (classy)
        return




if __name__ == "__main__":
    redditID = sys.argv[1]
    if len(redditID == 6):
        bot = RedditBot("Humor 1.0")
        bot.initializeBot(config.BOT_USERNAME, config.BOT_PASSWORD)
        bot.makeComment(redditID)
