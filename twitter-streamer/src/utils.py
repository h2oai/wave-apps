from h2o_wave import Q
from .config import Configuration

config = Configuration()


def check_credentials_empty(q: Q):
    """
    Check whether credentials are empty or not

    :param q: Query context

    :return: True if credential not empty else false
    """
    return "" in [q.args.consumer_key, q.args.consumer_secret, q.args.access_token, q.args.access_token_secret]