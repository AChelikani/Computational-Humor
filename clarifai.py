import requests
import config
import sys

class Clarifai(object):
    def __init__(self, authToken):
        self.auth = authToken

    # Returns sorted array of (tag, prob)
    def makeRequest(self, url):
        header = {'Authorization' : 'Bearer ' + self.auth}
        response = requests.get(url, headers=header).json()
        tmp = response["results"][0]["result"]["tag"]
        return zip(tmp["classes"], tmp["probs"])



if __name__ == "__main__":
    clarifai = Clarifai(config.CLARIFAI_AUTH)
    img_url = sys.argv[1]
    url = "https://api.clarifai.com/v1/tag/?url=" + img_url
    print clarifai.makeRequest(url)
