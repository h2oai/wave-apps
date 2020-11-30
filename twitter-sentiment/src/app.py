from h2o_wave import Q, site, app, ui, main

import itertools
from .config import Configuration
from .tweet_analyser import TweetAnalyser

access_token = '955862386388344832-7ZYvXCkpyFO6Pbhh93Od4O94E5ga1t4'
access_token_secret = 'OfRg3O4SnrOinda7VeOTjfIBfWe9uzmRJd5IBEsQOdvvl'
config = Configuration()
tweet_analyser = TweetAnalyser(config.consumer_key, config.consumer_secret)


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
        # ui.Buttons(
        ui.button(name="search", label="search", primary=True)]))


async def initialize_page(q: Q):
    if not q.client.initalized:
        q.args.text = 'AI'
        q.args.search = True
        q.client.initalized = True
        (q.app.header_png,) = await q.site.upload([config.image_path])
        tweet_analyser.set_auth_handler_access_token(access_token, access_token_secret)
        tweet_analyser.create_tweepy_api_instance()

        q.client.app_initialized = True

    q.page.drop()

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

    home_content(q)


async def list_tweets_for_hashtag(q):
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
    await initialize_page(q)
    if q.args.search:
        await list_tweets_for_hashtag(q)

    await q.page.save()
