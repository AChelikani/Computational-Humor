# Computational-Humor
Using machine learning to deliver funny captions for pictures.

## Installation
Run `pip install praw`

## Clarifai API Setup
Make an account on Clarifai, get an access token then run:
```curl "https://api.clarifai.com/v1/tag/?model=general-v1.3&url={img url}" \
  -H "Authorization: Bearer {access token}"```

## Execution
Run `python reddit.py`
