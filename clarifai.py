import requests
import config
import sys

class Clarifai(object):
    def __init__(self, authToken):
        self.auth = authToken

    # Returns sorted array of (tag, prob)
    def makeRequest(self, url):
        url = "https://api.clarifai.com/v1/tag/?url=" + url + ".png"
        header = {'Authorization' : 'Bearer ' + self.auth}
        response = requests.get(url, headers=header).json()
        tmp = response["results"][0]["result"]["tag"]
        # Probs stored in tmp["probs"]
        return tmp["classes"]
