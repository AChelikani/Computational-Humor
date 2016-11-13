import re
import words


def populateFunny(comments, syns):
    '''
    Populates funny words by cleaning the comments and removing tags.

    Arguments:
        comments    -- nested list of comments
        syns        -- image tags and their synonyms

    Return value:
        Set of funny words (comments - tags)
    '''
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
        funny.extend(tmp)

    return set(funny)
