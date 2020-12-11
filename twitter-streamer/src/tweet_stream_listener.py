import tweepy
import json


class TwitterStreamListener(tweepy.StreamListener):
    """ A listener handles tweets that are received from the stream.
    This is a basic listener that just prints received tweets to stdout.
    """

    def __init__(self, tweets):
        self.tweets = tweets


    def on_data(self, data):
        json_data = json.loads(data)
        self.tweets.append(json_data)

    def on_error(self, status):
        if status == 420:
            print('Enhance Your Calm; The App Is Being Rate Limited For Making Too Many Requests')
            return True
        else:
            print('Error {}n'.format(status))
            return True