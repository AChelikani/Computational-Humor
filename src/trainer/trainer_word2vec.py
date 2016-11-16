import gensim

model = gensim.models.Word2Vec.load_word2vec_format('./GoogleNews-vectors-negative300.bin', binary=True)

class Relation:
    def __init__(self, pos, neg):
        self.pos = pos
        self.neg = neg

    def get_similar(self):
        return model.most_similar(positive=self.pos, negative=self.neg)

    def __str__(self):
        x = '+'.join(self.pos)
        if len(self.neg) > 0:
            x += '-' + '-'.join(self.neg)
        return x

    def __add__(self, other):
        self.pos.append(other.word)
        return Relation(self.pos, self.neg)

    def __sub__(self, other):
        self.neg.append(other.word)
        return Relation(self.pos, self.neg)


class Word:
    def __init__(self, word):
        self.word = word
        self.vec = model[word]

    def __str__(self):
        return self.word

    def __add__(self, other):
        pos = [self.word, other.word]
        return Relation(pos, [])

    def __sub__(self, other):
        pos = [self.word]
        neg = [other.word]
        return Relation(pos, neg)
