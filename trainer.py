import requests
import config

class Trainer(object):
    def __init__(self):
        pass

    def populateSynonyms(self, arr):
        syns = set([])
        for word in arr:
            syns.add(word)
            resp = self.getSynonyms(word)
            for syn in resp:
                syns.add(syn)
        return syns

    def getSynonyms(self, word):
        url = "http://words.bighugelabs.com/api/2/" + config.WORD_AUTH + "/" + word + "/json"
        response = requests.get(url).json()
        for key in response:
            if (key == "noun"):
                return response[key]["syn"]
        return []

if __name__ == "__main__":
    trainer = Trainer()
    trainer.getSynonyms("help")
