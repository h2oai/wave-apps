from tweepy import Cursor
from tweepy.api import API
from tweepy.auth import OAuthHandler
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


class TweetAnalyser:
    """
        Wrapper for Tweepy API and vaderSentiment.vaderSentiment

        TweetAnalyser builds an abstraction between tweepy api and the twitter sentiment app
        giving the developer freedom to integrate tweepy api and vaderSentiment.vaderSentiment
        with a minimal change to the app code.
        """

    def __init__(self, consumer_key, consumer_secret):
        self.analyser = SentimentIntensityAnalyzer()
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.auth_handler = None
        self.api = None

    def create_auth_handler(self, consumer_key, consumer_secret):
        """
        Creates Tweepy OAuthHandler
        """
        self.auth_handler = OAuthHandler(consumer_key, consumer_secret)

    def set_auth_handler_access_token(self, access_token, access_token_secret):
        """
        Updates access token of the Tweepy OAuthHandler
        """
        self.auth_handler.set_access_token(access_token, access_token_secret)

    def create_tweepy_api_instance(self):
        """
        Creates Tweepy API instance
        """
        self.api = API(self.auth_handler, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    def search_tweets(self, q, lang="en", rpp=100, items=16):
        """
        Return iterator for items in each page
        """
        return Cursor(self.api.search, q, lang, rpp).items(items)

    def get_polarity_scores(self, text):
        """
        Return a float for sentiment strength based on the input text.
        Positive values are positive valence, negative value are negative
        valence.

        :param text: the input text
        :return: a float value sentiment strength
        """
        return self.analyser.polarity_scores(text)
