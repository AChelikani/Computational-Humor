import requests
import config

class Clarifai(object):
    def __init__(self, authToken):
        self.auth = authToken

    def makeRequest(self, url):
        header = {'Authorization' : 'Bearer ' + self.auth}
        response = requests.get(url, headers=header)
        return response.json()



if __name__ == "__main__":
    clarifai = Clarifai(config.AUTH)
    url = "https://api.clarifai.com/v1/tag/?url=https://samples.clarifai.com/metro-north.jpg"
    print clarifai.makeRequest(url)
