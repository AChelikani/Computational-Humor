import argparse
import praw

# Class for data object
'''
Image url, title
'''
class DataObject(object):
    def __init__(self, title, url, comments):
        self.imgurl = url
        self.title = title
        self.comments = comments

# Wrapper class for Reddit API
class Reddit(object):
    def __init__(self, userAgent):
        self.userAgent = userAgent
        self.connected = False

    # Establish connection
    def connect(self):
        self.reddit = praw.Reddit(user_agent=self.userAgent)
        self.connected = True

    # Check if connection is established
    def isConnected(self):
        return self.connected

    # Get <lim <= 1000> postings from given subreddit
    # @rtype: array of DataObjects
    def getSubreddit(self, subName, lim):
        if (self.isConnected()):
            data = []
            results = self.reddit.get_subreddit(subName).get_hot(limit=lim)
            for item in results:
                data.append(DataObject(item.title, item.url, item.comments))
            return data
        return None


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("subreddit")
    parser.add_argument("count", type=int)
    args = parser.parse_args()
    reddit = Reddit("Computation Humor 1.0")
    reddit.connect()
    x = reddit.getSubreddit(args.subreddit, args.count)
    for post in x:
        print post.title
        print "================================================================================"
