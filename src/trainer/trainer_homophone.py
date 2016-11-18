import requests


def getHomophones(word):
    url = "http://api.datamuse.com/words?rel_hom=" + word
    homophones = []
    try:
        response = requests.get(url).json()
        for res in response:
            homophones.append([res["word"], res["score"]])
        return homophones
    except Exception:
        pass
    return []


if __name__ == "__main__":
    print getHomophones("course")
