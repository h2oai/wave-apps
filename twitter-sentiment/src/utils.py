from h2o_wave import Q
from .config import Configuration

config = Configuration()


def derive_sentiment_status(compound):
    """
    Derives the status of the sentiment

    :param compound

    :return: status of the sentiment
    """
    if compound > 0:
        return "Positive"
    elif compound == 0:
        return "Neutral"
    else:
        return "Negative"


def derive_sentiment_message_type(compound):
    """
    Derives the type of the message based status of the sentiment

    :param compound

    :return: type of the message
    """
    if compound > 0:
        return "success"
    elif compound == 0:
        return "info"
    else:
        return "error"


def check_credentials_empty(q: Q):
    """
    Check whether credentials are empty or not

    :param q: Query context

    :return: True if credential not empty else false
    """
    return "" in [q.args.consumer_key, q.args.consumer_secret, q.args.access_token, q.args.access_token_secret]

def map_popularity_score_keys(popularity):
    """
    Maps popularity score keys to be more meaningful

    :param popularity: popularity scores of the analysis

    :return: Mapped dictionary of the scores
    """

    return dict((config.popularity_terms[key], value) for (key, value) in popularity.items())