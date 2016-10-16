
class DataObject(object):
    def __init__(self, title, url, comments):
        self.imgurl = url
        self.title = title
        self.comments = comments

def readfile(filename):
    with open(filename) as f:
        posts = []
        for line in f:
            data = line.split(",")
            title = data[0]
            imgurl = data[1]
            comments = data[2:]
            posts.append(DataObject(title, imgurl, comments))
    return posts
