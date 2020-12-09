from h2o_wave import Q, app, ui, main

from .config import Configuration
from .plots import (
    convert_plot_to_html,
    generate_figure_pie_of_target_percent
)
from .tweet_analyser import TweetAnalyser
from .utils import derive_sentiment_status, derive_sentiment_message_type, check_credentials_empty, \
    map_popularity_score_keys

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
    # The meta card's 'zones' attribute defines placeholder zones to lay out cards for different viewport sizes.
    # We define four layout schemes here.
    q.page['twitter_app'] = ui.meta_card(box='', layouts=[
        ui.layout(
            # If the viewport width >= 0:
            breakpoint='xs',
            width='400px',
            zones=[
                # 80px high header
                ui.zone('header', size='80px'),
                ui.zone('search_bar', direction=ui.ZoneDirection.ROW, size=80, zones=[
                    # 400px wide search_text_area
                    ui.zone('search_text_area', size='400px', direction=ui.ZoneDirection.ROW),
                ]),
                ui.zone('search_button_area', direction=ui.ZoneDirection.ROW, size=80, zones=[
                    # 400px wide search_button
                    ui.zone('search_button', size='400px', direction=ui.ZoneDirection.ROW),
                ]),
                # Use remaining space for body
                ui.zone('body', direction=ui.ZoneDirection.COLUMN, size='450px',
                        zones=create_twitter_card_slots(12, 1)),
            ]
        ),
        ui.layout(
            # If the viewport width >= 768:
            breakpoint='m',
            width='768px',
            zones=[
                # 80px high header
                ui.zone('header', size='80px'),
                ui.zone('search_bar', direction=ui.ZoneDirection.ROW, size=80, zones=[
                    # 600px wide search_text_area
                    ui.zone('search_text_area', size='600px', direction=ui.ZoneDirection.ROW),
                    # 160px wide search_button
                    ui.zone('search_button', size='200px', direction=ui.ZoneDirection.ROW),
                ]),
                # Use remaining space for body
                ui.zone('body', direction=ui.ZoneDirection.COLUMN, size='800px', zones=create_twitter_card_slots(6, 2))
            ]
        ),
        ui.layout(
            # If the viewport width >= 1200:
            breakpoint='xl',
            width='1200px',
            zones=[
                # 80px high header
                ui.zone('header', size='80px'),
                ui.zone('search_bar', direction=ui.ZoneDirection.ROW, size=80, zones=[
                    # 1000px wide search_text_area
                    ui.zone('search_text_area', size='1000px', direction=ui.ZoneDirection.ROW),
                    # 215px wide search_button
                    ui.zone('search_button', size='215px', direction=ui.ZoneDirection.ROW),
                ]),
                # Use remaining space for body
                ui.zone('body', direction=ui.ZoneDirection.COLUMN, size='1200px', zones=create_twitter_card_slots(4, 3))
            ]
        ),
        ui.layout(
            # If the viewport width >= 1600:
            breakpoint='1600px',
            width='1600px',
            zones=[
                # 80px high header
                ui.zone('header', size='80px'),
                ui.zone('search_bar', direction=ui.ZoneDirection.ROW, size=80, zones=[
                    # 1400px wide search_text_area
                    ui.zone('search_text_area', size='1400px', direction=ui.ZoneDirection.ROW),
                    # 230px wide search_button
                    ui.zone('search_button', size='230px', direction=ui.ZoneDirection.ROW),
                ]),
                # Use remaining space for body
                ui.zone('body', direction=ui.ZoneDirection.COLUMN, size='1600px', zones=create_twitter_card_slots(3, 4))
            ]
        )
    ])
    q.page['header'] = ui.header_card(
        box='header',
        title=config.title,
        subtitle=config.subtitle,
        icon=config.icon,
        icon_color=config.color,
    )

    q.page["search_text_area"] = ui.form_card(box=ui.boxes('search_text_area'), items=[
        ui.textbox(name='text',
                   label='',
                   placeholder='#h2oai',
                   value=q.args.text, multiline=False, trigger=False)])

    q.page["search_button"] = ui.form_card(box=ui.boxes('search_button'), items=[
        ui.button(name="search", label="search", primary=True)])

    for tweet_count in range(1, config.max_tweet_count + 1):
        q.page[f'twitter_card_{tweet_count}'] = ui.form_card(box=f'content_{tweet_count}', items=[])


def create_twitter_card_slots(row_count, column_count):
    return [
        ui.zone(f'row_' + str(row), direction=ui.ZoneDirection.ROW, size='450px', zones=[
            ui.zone('content_' + str((row * column_count) + column), direction=ui.ZoneDirection.ROW, size='400px') for
            column in range(1, column_count + 1)
        ]) for row in range(0, row_count)]


async def initialize_page(q: Q):
    q.page['twitter_app'].dialog = None
    if not q.client.initialized:
        q.args.text = config.default_search_text
        q.args.search = True
        (q.app.header_png,) = await q.site.upload([config.image_path])
        q.client.tweet_analyser = TweetAnalyser(q.args.consumer_key, q.args.consumer_secret)
        q.client.tweet_analyser.create_auth_handler(q.args.consumer_key, q.args.consumer_secret)
        q.client.tweet_analyser.set_auth_handler_access_token(q.args.access_token, q.args.access_token_secret)
        q.client.tweet_analyser.create_tweepy_api_instance()
        home_content(q)
        q.client.initialized = True
        q.client.app_initialized = True

    await list_tweets_for_hashtag(q)


def capture_credentials(q: Q):
    q.page['twitter_app'] = ui.meta_card(box='')
    q.page['twitter_app'].dialog = ui.dialog(title='Twitter Credentials', primary=True, items=[
        ui.markup(name="request_access", visible=True, content=config.ask_for_access_text),
        ui.textbox(name='consumer_key', label='Consumer Key', required=True, password=True),
        ui.textbox(name='consumer_secret', label='Consumer Secret', required=True, password=True),
        ui.textbox(name='access_token', label='Access Token', required=True, password=True),
        ui.textbox(name='access_token_secret', label='Access Token Secret', required=True, password=True),
        ui.buttons([ui.button(name='submit', label='Configure', primary=True, tooltip="")])
    ])


async def list_tweets_for_hashtag(q):
    values, text = search_tweets(q)
    tweet_count = 1

    for tweet in text:
        popularity_score = values[tweet]
        q.page[f'twitter_card_{tweet_count}'].items = [
            ui.message_bar(type=f"{derive_sentiment_message_type(popularity_score['compound'])}",
                           text=f"Sentiment - {derive_sentiment_status(popularity_score['compound'])}"),
            ui.text(content=tweet[:200]),
            ui.frame(content=convert_plot_to_html(
                generate_figure_pie_of_target_percent(map_popularity_score_keys(popularity_score)), "cdn", False),
                width='100%', height='60%')
        ]
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
