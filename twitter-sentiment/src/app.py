import os
from typing import Tuple
from h2o_wave import Q, app, ui, main, data

from .tweet_analyser import TweetAnalyser

def configure_page(q: Q, bypass_login):
    q.page['twitter_app'].dialog = None
    q.page['search'] = ui.form_card(box='search', items=[ui.textbox(name='search', trigger=True, icon='Search')])
    q.client.tweet_analyser = TweetAnalyser(q.app.env_vars[0], q.app.env_vars[1], q.app.env_vars[2], q.app.env_vars[3]) if bypass_login else TweetAnalyser(q.args.access_token, q.args.access_token_secret, q.args.consumer_key, q.args.consumer_secret)


def init(q: Q):
    q.app.env_vars.append(os.environ.get("ACCESS_TOKEN"))
    q.app.env_vars.append(os.environ.get("ACCESS_TOKEN_SECRET"))
    q.app.env_vars.append(os.environ.get("CONSUMER_KEY"))
    q.app.env_vars.append(os.environ.get("CONSUMER_SECRET"))
    q.page['header'] = ui.header_card(
        box='header',
        title='Twitter Sentiment',
        subtitle='Searches twitter hashtags and sentiment analysis',
        icon='UpgradeAnalysis',
        icon_color='#00A8E0',
    )
    if not (None in q.app.env_vars):
        # Existing login credentials in environment variables --> bypass login 
        configure_page(q, True)
        search_tweets(q)
        q.page['twitter_app'] = ui.meta_card(
            box='',
            title='Twitter Sentiment',
            layouts=[ui.layout('xs', zones=[
                ui.zone('header'),
                ui.zone('search'),
                ui.zone('twitter_cards', direction=ui.ZoneDirection.ROW, wrap='stretch', justify='center')
            ])]
        )
    else:
        # Missing login credentials in environment variables --> required login 
        q.page['twitter_app'] = ui.meta_card(
            box='',
            title='Twitter Sentiment',
            dialog= ui.dialog(title='Twitter Credentials', primary=True, items=[
                ui.markup('Apply for access : <a href="https://developer.twitter.com/en/apply-for-access" target="_blank">Visit developer.twitter.com!</a>'),
                ui.textbox(name='consumer_key', label='Consumer Key', required=True, password=True),
                ui.textbox(name='consumer_secret', label='Consumer Secret', required=True, password=True),
                ui.textbox(name='access_token', label='Access Token', required=True, password=True),
                ui.textbox(name='access_token_secret', label='Access Token Secret', required=True, password=True),
                ui.buttons(items=[ui.button(name='configure', label='Configure', primary=True)], justify='end')
            ]),
            layouts=[ui.layout('xs', zones=[
                ui.zone('header'),
                ui.zone('search'),
                ui.zone('twitter_cards', direction=ui.ZoneDirection.ROW, wrap='stretch', justify='center')
            ])]
        )

def get_sentiment(polarity) -> Tuple[str, str]:
    compound = polarity['compound']
    if compound > 0:
        return 'success', 'Positive'
    elif compound == 0:
        return 'warning', 'Neutral'
    else:
        return 'error', 'Negative'


def search_tweets(q: Q):
    # TODO: Remove after https://github.com/h2oai/wave/issues/150 resolved.
    q.page['search'].items[0].textbox.value = q.args.search or 'AI'
    for i, tweet in enumerate(q.client.tweet_analyser.search_tweets(q=q.args.search or 'AI')):
        if not tweet.retweeted:
            polarity = q.client.tweet_analyser.get_polarity_scores(tweet.text) 
            message_type, sentiment = get_sentiment(polarity)
            plot_rows = [
              (polarity['neg'], 'Negative'),
              (polarity['neu'], 'Neutral'),
              (polarity['pos'], 'Positive'),
            ]
            q.page[f'twitter_card_{i}'] = ui.form_card(box=ui.box('twitter_cards', width='400px'), items=[
                ui.message_bar(type=message_type, text=f'Sentiment - {sentiment}'),
                ui.visualization(
                    plot=ui.plot([ui.mark(type='interval', x='=sentiment', y='=value', color='=sentiment', color_range='$red $yellow $green')]),
                    data=data(['value', 'sentiment'], rows=plot_rows, pack=True),
                ),
                ui.text(f'_{tweet.text}_'),
            ])


@app('/')
async def serve(q: Q):
    q.app.env_vars = []
    if not q.client.initialized:
        init(q)
        q.client.initialized = True
    if q.args.configure:
        # Grant access after login credentials are manually passed
        configure_page(q, False)
        search_tweets(q)
    elif  q.args.search:
      search_tweets(q)

    await q.page.save()
