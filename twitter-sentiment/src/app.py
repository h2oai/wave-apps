from h2o_wave import Q, app, ui, main

import itertools
from .config import Configuration
from .plots import (
    convert_plot_to_html,
    generate_figure_pie_of_target_percent
)
from .tweet_analyser import TweetAnalyser
from .utils import derive_sentiment_status, derive_sentiment_message_type, check_credentials_empty, map_popularity_score_keys

config = Configuration()


def search_tweets(q: Q):
    tweets = {}
    texts = []
    tweet_count = 0
    # for tweet in api.search(q=tag, lang="en", rpp=100).items(MAX_TWEETS):
    for tweet in q.client.tweet_analyser.search_tweets(q=q.args.text, lang="en", rpp=100, items=config.max_tweet_count):
        if not tweet.retweeted:  # and ('RT @' not in tweet.text):
            texts.append(tweet.text)
            tweet_count = tweet_count + 1
        else:
            break

    texts = list(set(texts))
    for t in texts:
        tweets[t] = q.client.tweet_analyser.get_polarity_scores(t)

    return tweets, texts


def home_content(q: Q):
    q.page["title"] = ui.header_card(
        box=config.boxes["banner"],
        title=config.title,
        subtitle=config.subtitle,
        icon=config.icon,
        icon_color=config.color,
    )

    q.page.add("search_tab", ui.form_card(box=config.boxes["search_tab"], items=[
        ui.textbox(name='text',
                   label='',
                   placeholder='#h2oai',
                   value=q.args.text, multiline=False, trigger=False)]))

    q.page.add("search_click", ui.form_card(box=config.boxes["search_click"], items=[
        ui.button(name="search", label="search", primary=True)]))


async def initialize_page(q: Q):
    q.page['credentials'].dialog = None
    if not q.client.initialized:
        q.args.text = config.default_search_text
        q.args.search = True
        (q.app.header_png,) = await q.site.upload([config.image_path])
        q.client.tweet_analyser = TweetAnalyser(q.args.consumer_key, q.args.consumer_secret)
        q.client.tweet_analyser.create_auth_handler(q.args.consumer_key, q.args.consumer_secret)
        q.client.tweet_analyser.set_auth_handler_access_token(q.args.access_token, q.args.access_token_secret)
        q.client.tweet_analyser.create_tweepy_api_instance()
        q.client.initialized = True
        q.client.app_initialized = True

    await list_tweets_for_hashtag(q)


def capture_credentials(q: Q):
    home_content(q)
    q.page['credentials'] = ui.meta_card(box=config.boxes['credentials'])
    q.page['credentials'].dialog = ui.dialog(title='Twitter Credentials', primary=True, items=[
        ui.markup(name="request_access", visible=True, content=config.ask_for_access_text),
        ui.textbox(name='consumer_key', label='Consumer Key', required=True, password=True),
        ui.textbox(name='consumer_secret', label='Consumer Secret', required=True, password=True),
        ui.textbox(name='access_token', label='Access Token', required=True, password=True),
        ui.textbox(name='access_token_secret', label='Access Token Secret', required=True, password=True),
        ui.buttons([ui.button(name='submit', label='Configure', primary=True, tooltip="")])
    ])


async def list_tweets_for_hashtag(q):
    home_content(q)
    values, text = search_tweets(q)
    tweet_count = 0
    boxes = [' '.join(i) for i in list(itertools.product(config.tweet_row_indexes, config.tweet_column_indexes))]
    for tweet in text:
        popularity_score = values[tweet]
        print(values[tweet])
        row, column = boxes[tweet_count].split(' ')
        plot_row = int(row) + 2
        q.page.add(f'wrapper_{column}_{row}', ui.form_card(box=f'{column} {row} 3 6', items=[
            ui.message_bar(type=f"{derive_sentiment_message_type(popularity_score['compound'])}",
                           text=f"Sentiment - {derive_sentiment_status(popularity_score['compound'])}"),
            ui.text(content=tweet)
        ]))

        q.page.add(f'plot_{column}_{row}', ui.frame_card(
            box=f'{column} {plot_row} 3 4',
            title="",
            content=convert_plot_to_html(generate_figure_pie_of_target_percent(map_popularity_score_keys(popularity_score)), "cdn", False),
        ))
        tweet_count = tweet_count + 1


@app('/')
async def serve(q: Q):
    if q.args.submit:
        if check_credentials_empty(q):
            capture_credentials(q)
        else:
            await initialize_page(q)
    elif q.args.search:
        await list_tweets_for_hashtag(q)
    else:
        capture_credentials(q)

    await q.page.save()
