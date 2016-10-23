import requests
import config

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
    url = "https://api.clarifai.com/v1/tag/?url=https://samples.clarifai.com/metro-north.jpg"
    print clarifai.makeRequest(url)
