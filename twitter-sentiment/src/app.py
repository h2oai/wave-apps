from h2o_wave import Q, app, ui, main, data

from .tweet_analyser import TweetAnalyser


@app('/')
async def serve(q: Q):
    if not q.client.initialized:
        q.page['header'] = ui.header_card(
            box='header',
            title='Twitter Sentiment',
            subtitle='Searches twitter hashtags and sentiment analysis',
            image='https://www.h2o.ai/wp-content/themes/h2o2018/templates/dist/images/h2o_logo.svg',
            items=[ui.textbox(name='search', trigger=True, icon='Search', width='400px', placeholder='Search tweets')]
        )
        q.page['twitter_app'] = ui.meta_card(box='', title='Twitter Sentiment', layouts=[ui.layout('xs', zones=[
            ui.zone('header'),
            ui.zone('twitter_cards', direction=ui.ZoneDirection.ROW, wrap='stretch', justify='center')
        ])])
        q.client.tweet_analyser = TweetAnalyser()
        q.client.initialized = True

    for i, tweet in enumerate(q.client.tweet_analyser.search_tweets(q=q.args.search or 'AI')):
        if not tweet.retweeted:
            polarity = q.client.tweet_analyser.get_polarity_scores(tweet.text)
            compound = polarity['compound']
            if compound > 0:
                message_type, sentiment = 'success', 'Positive'
            elif compound == 0:
                message_type, sentiment = 'warning', 'Neutral'
            else:
                message_type, sentiment = 'error', 'Negative'
            q.page[f'twitter_card_{i}'] = ui.form_card(box=ui.box('twitter_cards', width='400px'), items=[
                ui.message_bar(type=message_type, text=f'Sentiment - {sentiment}'),
                ui.visualization(
                    plot=ui.plot([ui.mark(type='interval', x='=sentiment', y='=value', color='=sentiment',
                                          color_range='$red $yellow $green')]),
                    data=data(['value', 'sentiment'], pack=True,
                              rows=[(polarity['neg'], 'Negative'), (polarity['neu'], 'Neutral'),
                                    (polarity['pos'], 'Positive')]),
                ),
                ui.text(f'_{tweet.text}_'),
            ])

    await q.page.save()
