import requests
import config
import sys

class Clarifai(object):
    '''
    Wrapper class for Clarifai API.
    '''

    def __init__(self, authToken):
        self.auth = authToken

    def makeRequest(self, url):
        '''
        Given an url, returns a sorted array of tuples (tag, probability).
        '''
        url = "https://api.clarifai.com/v1/tag/?url=" + url + ".png"
        header = {'Authorization' : 'Bearer ' + self.auth}
        response = requests.get(url, headers=header).json()
        # Probabilities are stored in tmp["probs"].
        tmp = response["results"][0]["result"]["tag"]
    
        return tmp["classes"]
