from h2o_wave import Q, site, app, ui, main

import itertools
from .config import Configuration
from .tweet_analyser import TweetAnalyser

config = Configuration()
tweet_analyser = None


def texts(tag):
    tws = {}
    texts = []
    cc = 0
    # for tweet in api.search(q=tag, lang="en", rpp=100).items(MAX_TWEETS):
    for tweet in tweet_analyser.search_tweets(q=tag, lang="en", rpp=100, items=16):
        if (not tweet.retweeted) and cc < 25:  # and ('RT @' not in tweet.text):
            texts.append(tweet.text)
            cc = cc + 1
        else:
            break

    texts = list(set(texts))
    for t in texts:
        score = tweet_analyser.get_polarity_scores(t)
        sc = score.copy()
        sc.pop('compound', None)
        if sc['pos'] < sc['neg']:
            m = 'neg'
        else:
            m = 'pos'
        mm = {'neu': 'Neutral', 'pos': 'Postive', 'neg': 'Negative'}
        tws[t] = (mm[m], sc)
    return (tws, texts)


def home_content(q: Q):
    q.page.add("search_tab", ui.form_card(box=config.boxes["search_tab"], items=[
        ui.textbox(name='text',
                   label='',
                   placeholder='#h2oai',
                   value=q.args.text, multiline=False, trigger=False)]))

    q.page.add("search_click", ui.form_card(box=config.boxes["search_click"], items=[
        ui.button(name="search", label="search", primary=True)]))


async def initialize_page(q: Q):
    q.page['credentials'].dialog = None
    if not q.client.initalized:
        q.args.text = 'AI'
        q.args.search = True
        q.client.initalized = True
        (q.app.header_png,) = await q.site.upload([config.image_path])
        global tweet_analyser
        tweet_analyser = TweetAnalyser(q.args.consumer_key, q.args.consumer_secret)
        tweet_analyser.set_auth_handler_access_token(q.args.access_token, q.args.access_token_secret)
        tweet_analyser.create_tweepy_api_instance()
        q.client.app_initialized = True

    await list_tweets_for_hashtag(q)


def capture_credentials(q: Q):
    q.page["title"] = ui.header_card(
        box=config.boxes["banner"],
        title=config.title,
        subtitle=config.subtitle,
        icon=config.icon,
        icon_color=config.color,
    )

    q.page["nav_bar"] = ui.form_card(
        box=config.boxes["navbar"],
        items=[],
    )

    q.page['credentials'] = ui.meta_card(box='-1 -1 -1 -1')
    q.page['credentials'].dialog = ui.dialog(title='Twitter Credentials', items=[
        ui.textbox(name='consumer_key', label='Consumer Key', required=True),
        ui.textbox(name='consumer_secret', label='Consumer Secret', required=True),
        ui.textbox(name='access_token', label='Access Token', required=True),
        ui.textbox(name='access_token_secret', label='Access Token Secret', required=True),
        ui.buttons([ui.button(name='submit', label='Configure', primary=True)])
    ])


async def list_tweets_for_hashtag(q):
    home_content(q)
    q.user.text = q.args.text
    values, text = texts(q.user.text)
    cc = 0
    boxes = [' '.join(i) for i in list(itertools.product(['3', '5', '7', '9', '11'], ['1', '4', '7', '10']))]
    for t in text:
        print(t)
        val = values[t]
        if val[0] == 'Negative':
            color = '$red'
        elif val[0] == 'Positive':
            color = '$blue'
        else:
            color = '$green'

        j, i = boxes[cc].split(' ')
        width = 3 if not i == '10' else '-1'
        q.page.add(f'example_{i}_{j}', ui.large_bar_stat_card(
            box=f'{i} {j} {width} 2',
            title=f'Sentiment - {val[0]}',
            value='={{intl foo minimum_fraction_digits=2 maximum_fraction_digits=2}}',
            value_caption='Negative',
            aux_value='={{intl bar minimum_fraction_digits=2 maximum_fraction_digits=2}}',
            aux_value_caption='Positive',
            plot_color=color,
            progress=1,
            data=dict(foo=val[1]['neg'], bar=val[1]['pos']),
            caption=t,
        ))
        cc = cc + 1


@app('/')
async def serve(q: Q):
    if q.args.submit:
        await initialize_page(q)
    elif q.args.search:
        await list_tweets_for_hashtag(q)
    else:
        capture_credentials(q)

    await q.page.save()
