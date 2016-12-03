# Computational-Humor
Using machine learning to deliver funny captions for pictures.

## Installation
Run `pip install praw`

## Setup
Make a local file `src/config.py` with the following:

```python
CLARIFAI_AUTH = {access token}
WORD_AUTH = {words.bighugelabs.com token}
SIM_AUTH = {https://dandelion.eu token}
BOT_USERNAME = {reddit account}
BOT_PASSWORD = {reddit password}
```

## Execution
Run `python reddit.py`
