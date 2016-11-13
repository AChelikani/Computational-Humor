import argparse
import praw
from collections import deque

class DataObject(object):
    '''
    Data object class that stores a post's title, url, and comments.
    '''

    def __init__(self, title, url, comments):
        self.imgurl = url
        self.title = title
        self.comments = comments


class Reddit(object):
    '''
    Wrapper class for Reddit API.
    '''

    def __init__(self, userAgent):
        self.userAgent = userAgent
        self.connected = False

    def connect(self):
        '''
        Establish connection.
        '''
        self.reddit = praw.Reddit(user_agent=self.userAgent)
        self.connected = True

    def isConnected(self):
        '''
        Checks if connection is established.
        '''
        return self.connected

    def flattenComments(self, comments):
        '''
        Flattens comments.
        '''
        return praw.helpers.flatten_tree(comments)

    def getCommentsById(self, postID):
        '''
        Gets comments from a specific post by its ID.
        '''
        comments = []
        votes = []

        if (self.isConnected()):
            submission = self.reddit.get_submission(submission_id=postID)
            comments.append(submission.title)
            votes.append(submission.ups)
            imgUrl = submission.url
            tmp = []
            tmpVotes = []
            flat_comments = self.flatten_comments(submission.comments)

            for comment in flat_comments:
                if hasattr(comment, 'body') and hasattr(comment, 'score'):
                    tmp.append(comment.body)
                    tmpVotes.append(comment.score)

            tmp = sorted(tmp, reverse=True)
            comments.extend(tmp[:5])
            votes.extend(tmpVotes[:5])

            return comments, imgUrl, votes

        return [], ""

    def getSubreddit(self, subName, lim):
        '''
        Gets <lim <= 1000> posts from given subreddit as an array of DataObjects.
        '''
        if (self.isConnected()):
            data = []
            results = self.reddit.get_subreddit(subName).get_hot(limit=lim)
            x = 0

            for item in results:
                comments = deque()
                comments.extend(item.comments)
                topComments = []

                while len(topComments) < 5 and len(comments) > 0:
                    comment = comments.popleft()

                    if type(comment) is praw.objects.Comment:
                        topComments.append(comment)
                        comments.extend(comment.replies)

                if len(topComments) >= 5:
                    data.append(DataObject(item.title, item.url, topComments[:5]))
                    print x
                    x += 1

            return data

        return None


### Testing
if __name__ == "__main__":
    # parser = argparse.ArgumentParser()
    # parser.add_argument("subreddit")
    # parser.add_argument("count", type=int)
    # args = parser.parse_args()
    # reddit = Reddit("Computation Humor 1.0")
    # reddit.connect()
    # x = reddit.getSubreddit(args.subreddit, args.count)
    # with open(args.subreddit + ".txt", "w") as f:
    #     for post in x:
    #         print post.title
    #         print "================================================================================"
    #         comments = [comment.body.strip().replace("\n", " ").encode('utf-8') for comment in post.comments]
    #         f.write(post.title.encode('utf-8') + "," + post.imgurl.encode('utf-8') + "," + ",".join(comments) + "\n")

    reddit = Reddit("Computation Humor 1.0")
    reddit.connect()
    print reddit.getCommentsById("5a5zmh")
