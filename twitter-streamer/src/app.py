from h2o_wave import Q, app, ui, main
import collections
import time

from threading import Thread
from .utils import check_credentials_empty

import sys
import os

from tweepy import OAuthHandler, Stream, StreamListener
from .config import Configuration
from .tweet_stream_listener import TwitterStreamListener
from .word_cloud_util import plot_word_cloud, merge_to_single_text

config = Configuration()

tweets = collections.deque(maxlen=12)

def tweet_stream(q: Q, hashtag='AI'):
    twitter_stream_listener = TwitterStreamListener(tweets)
    auth = OAuthHandler(q.client.consumer_key, q.client.consumer_secret)
    auth.set_access_token(q.client.access_token, q.client.access_token_secret)
    stream = Stream(auth, twitter_stream_listener)
    stream.filter(track=[hashtag], is_async=True)
    q.client.twitter_stream = stream


async def initialize_page(q: Q):
    q.page['twitter_stream_app'].dialog = None
    if not q.client.initialized:
        q.args.text = config.default_search_text
        q.args.search = True
        (q.app.header_png,) = await q.site.upload([config.image_path])
        init_client_credentials(q)
        tweet_stream(q, config.default_search_text)
        # on_start(q, config.default_search_text)
        home_content(q)
        await create_dashboard(q, update_freq=10, keyword=config.default_search_text)
        q.client.initialized = True


def init_client_credentials(q):
    q.client.consumer_key = q.args.consumer_key
    q.client.consumer_secret = q.args.consumer_secret
    q.client.access_token = q.args.access_token
    q.client.access_token_secret = q.args.access_token_secret


def home_content(q: Q):
    # The meta card's 'zones' attribute defines placeholder zones to lay out cards for different viewport sizes.
    # We define four layout schemes here.
    q.page['twitter_stream_app'] = ui.meta_card(box='', layouts=[
        ui.layout(
            # If the viewport width >= 0:
            breakpoint='xs',
            width='400px',
            zones=[
                # 80px high header
                ui.zone('header', size='80px'),
                # Use remaining space for body
                ui.zone('body', direction=ui.ZoneDirection.ROW, zones=[
                    ui.zone('twitter_card', size='400px', direction=ui.ZoneDirection.COLUMN),
                ])
            ]
        ),
        ui.layout(
            # If the viewport width >= 768:
            breakpoint='m',
            width='768px',
            zones=[
                # 80px high header
                ui.zone('header', size='80px'),
                # Use remaining space for body
                ui.zone('body', direction=ui.ZoneDirection.ROW, zones=[
                    ui.zone('twitter_card', size='800px', direction=ui.ZoneDirection.COLUMN),
                ])
            ]
        ),
        ui.layout(
            # If the viewport width >= 1200:
            breakpoint='xl',
            width='1200px',
            zones=[
                # 80px high header
                ui.zone('header', size='80px'),
                # Use remaining space for body
                ui.zone('body', direction=ui.ZoneDirection.ROW, zones=[
                    ui.zone('twitter_card', size='600px', direction=ui.ZoneDirection.COLUMN),
                    ui.zone('word_cloud', direction=ui.ZoneDirection.COLUMN),
                ])
            ]
        ),
        ui.layout(
            # If the viewport width >= 1600:
            breakpoint='1600px',
            width='1600px',
            zones=[
                # 80px high header
                ui.zone('header', size='80px'),
                # Use remaining space for body
                ui.zone('body', direction=ui.ZoneDirection.ROW, zones=[
                    ui.zone('twitter_card', size='800px', direction=ui.ZoneDirection.COLUMN),
                    ui.zone('word_cloud', direction=ui.ZoneDirection.COLUMN),
                ])
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

    q.page['twitter_card'] = ui.form_card(box=ui.boxes('twitter_card'), items=[])
    q.page['word_cloud_card'] = ui.image_card(box=ui.boxes('word_cloud'), title='',
                                              type='png',
                                              image='')


def create_twitter_card_slots(row_count, column_count):
    return [
        ui.zone(f'row_{row}', direction=ui.ZoneDirection.ROW, size='450px', zones=[
            ui.zone(f'content_{(row * column_count) + column}', direction=ui.ZoneDirection.ROW, size='400px') for
            column in range(0, column_count)
        ]) for row in range(0, row_count)]


async def create_dashboard(q: Q, keyword, update_freq=0.0):
    items = [ui.text(content='') for i in range(1, tweets.maxlen)]
    large_pbs = q.page['twitter_card']
    large_pbs.items = items

    while update_freq > 0:
        time.sleep(update_freq)
        print(len(tweets))
        items = []
        for index, tweet in enumerate(tweets):
            items.append(
                ui.message_bar(type=ui.MessageBarType.INFO, text=f'Twitter user : {tweet["user"]["screen_name"]}'))
            items.append(ui.text(content=tweet['text']))
            items.append(ui.separator())

        large_pbs.items = items
        render_all_text_word_cloud(q, keyword)
        await q.page.save()


def capture_credentials(q: Q):
    q.page['header'] = ui.header_card(
        box=config.boxes['banner'],
        title=config.title,
        subtitle=config.subtitle,
        icon=config.icon,
        icon_color=config.color,
    )
    q.page['twitter_stream_app'] = ui.meta_card(box='')
    q.page['twitter_stream_app'].dialog = ui.dialog(title='Twitter Credentials', primary=True, items=[
        ui.markup(name="request_access", visible=True, content=config.ask_for_access_text),
        ui.textbox(name='consumer_key', label='Consumer Key', required=True, password=True),
        ui.textbox(name='consumer_secret', label='Consumer Secret', required=True, password=True),
        ui.textbox(name='access_token', label='Access Token', required=True, password=True),
        ui.textbox(name='access_token_secret', label='Access Token Secret', required=True, password=True),
        ui.buttons([ui.button(name='submit', label='Configure', primary=True, tooltip="")])
    ])


def on_start(q: Q, keyword):
    stream_thread = Thread(target=tweet_stream, args=[q, keyword])
    q.client.stream_thread = stream_thread
    stream_thread.start()


def on_shutdown():
    print("Stopping Application")
    python = sys.executable
    os.execl(python, python, *sys.argv)


def render_all_text_word_cloud(q: Q, hashtag):
    image = plot_word_cloud(merge_to_single_text(tweets))

    q.page['word_cloud_card'].image = image
    q.page['word_cloud_card'].title = f'WordCloud of {hashtag}'


@app('/', on_shutdown=on_shutdown)
async def serve(q: Q):
    if q.args.submit:
        if check_credentials_empty(q):
            capture_credentials(q)
        else:
            await initialize_page(q)
    else:
        capture_credentials(q)
    await q.page.save()
