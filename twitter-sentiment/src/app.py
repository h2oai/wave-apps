from h2o_wave import Q, app, ui, main

from .tweet_analyser import TweetAnalyser


@app('/')
async def serve(q: Q):
    if not q.app.initialized:
        q.app.positive, q.app.neutral, q.app.negative = await q.site.upload(
            ['static/positive.svg', 'static/neutral.svg', 'static/negative.svg'])
        q.app.initialized = True
    if not q.client.initialized:
        q.page['header'] = ui.header_card(
            box='header',
            title='Twitter Sentiment',
            subtitle='Searches twitter hashtags and sentiment analysis',
            image='https://www.h2o.ai/wp-content/themes/h2o2018/templates/dist/images/h2o_logo.svg',
            items=[ui.textbox(name='search', trigger=True, icon='Search', width='400px', value='AI')]
        )
        q.page['twitter_app'] = ui.meta_card(box='', title='Twitter Sentiment', layouts=[ui.layout('xs', zones=[
            ui.zone('header'),
            ui.zone('twitter_cards', direction=ui.ZoneDirection.ROW, wrap='stretch', justify='center')
        ])])
        q.client.tweet_analyser = TweetAnalyser()
        q.client.initialized = True

    for i, tweet in enumerate(q.client.tweet_analyser.search_tweets(q=q.args.search or 'AI')):
        if not tweet.retweeted:
            compound = q.client.tweet_analyser.get_polarity_scores(tweet.text)['compound']
            if compound > 0:
                sentiment = 'positive'
            elif compound == 0:
                sentiment = 'neutral'
            else:
                sentiment = 'negative'
            q.page[f'twitter_card_{i}'] = ui.profile_card(
                box=ui.box('twitter_cards', width='400px'),
                persona=ui.persona(title=tweet.user.name, image=tweet.user.profile_image_url),
                image=q.app[sentiment],
                items=[ui.text(f'_{tweet.text}_')],
                height='170px'
            )

    await q.page.save()
