from tweepy import Cursor
from tweepy.api import API
from tweepy.auth import OAuthHandler
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


class TweetAnalyser:

    def __init__(self, consumer_key, consumer_secret):
        self.analyser = SentimentIntensityAnalyzer()
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.auth_handler = self.create_auth_handler(consumer_key, consumer_secret)
        self.api = None

    def create_auth_handler(self, consumer_key, consumer_secret):
        return OAuthHandler(consumer_key, consumer_secret)

    def set_auth_handler_access_token(self, access_token, access_token_secret):
        self.auth_handler.set_access_token(access_token, access_token_secret)

    def create_tweepy_api_instance(self):
        self.api = API(self.auth_handler, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    def search_tweets(self, q, lang="en", rpp=100, items = 16):
        return Cursor(self.api.search, q, lang, rpp).items(items)

    def get_polarity_scores(self, t):
        return self.analyser.polarity_scores(t)
