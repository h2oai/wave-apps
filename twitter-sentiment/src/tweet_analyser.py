from tweepy import Cursor
from tweepy.api import API
from tweepy.auth import OAuthHandler
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

ACCESS_TOKEN = '2944447934-6KB33SzWsywpjYuibVLlKDFldCbYq0OcP7jJRg2'
ACCESS_TOKEN_SECRET = 'teBNYDJovG8lNrwUk8w2TWErR7gEaGRHTdI105dcw0yV5'
CONSUMER_KEY = 'TwgJUSNeivHHOJXLj9dUQzMOp'
CONSUMER_SECRET = 'cXHG8F298S5SYr0wVobZqZLH7qmOGyPghYGbH9Q6ZVb2KuchIr'


class TweetAnalyser:
    """
        Wrapper for Tweepy API and vaderSentiment.vaderSentiment

        TweetAnalyser builds an abstraction between tweepy api and the twitter sentiment app
        giving the developer freedom to integrate tweepy api and vaderSentiment.vaderSentiment
        with a minimal change to the app code.
        """

    def __init__(self):
        self.analyser = SentimentIntensityAnalyzer()
        self.auth_handler = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        self.auth_handler.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
        self.api = API(self.auth_handler, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    def search_tweets(self, q: str, lang='en', rpp=100, items=12):
        """
        Return iterator for items in each page
        """
        return Cursor(self.api.search, q, lang, rpp).items(items)

    def get_polarity_scores(self, text: str):
        """
        Return a float for sentiment strength based on the input text.
        Positive values are positive valence, negative value are negative
        valence.

        :param text: the input text
        :return: a float value sentiment strength
        """
        return self.analyser.polarity_scores(text)
