from h2o_wave import main, app, Q, ui, expando_to_dict
from wordcloud import WordCloud, STOPWORDS
from .config import Configuration

import io
import base64
import matplotlib.pyplot as plt

config = Configuration()
word_cloud = WordCloud(mode='RGBA', background_color=None, stopwords=set(STOPWORDS), min_font_size=10)


def plot_word_cloud(df, q: Q):
    figsize = (6, 3)
    width = 400
    height = 200
    if q.client.filters:
        figsize = (6, 6)
        width = 200
        height = 400

    word_cloud.height = height
    word_cloud.width = width
    word_cloud.generate(''.join(df))

    fig = plt.figure(figsize=figsize)
    plt.imshow(word_cloud)
    plt.axis('off')
    plt.tight_layout(pad=0)

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', transparent=True)
    buffer.seek(0)
    plt.close(fig)

    return base64.b64encode(buffer.read()).decode('utf-8')


def render_diff_word_cloud(q: Q):
    df = config.dataset

    for key, value in q.client.filters.items():
        df = df[df[key] == value]

    if len(df):
        # Remove when https://github.com/h2oai/wave/pull/611 merged.
        q.page['meta'].layouts[0].zones[1].zones[1].zones[1].size = '1'
        q.page['diff'] = ui.image_card(box='diff', title='Diff', type='png', image=plot_word_cloud(df[q.client.review], q))
    else:
        # TODO: Move into sidebar when https://github.com/h2oai/wave/pull/507 merged.
        q.page['diff'] = ui.form_card(box='diff', items=[ui.message_bar(type='warning', text='No reviews matching filter criteria!')])


def init(q: Q):
    q.page['meta'] = ui.meta_card(box='', title='Explain Ratings', layouts=[
        ui.layout(
            breakpoint='xs',
            zones=[
                ui.zone('header'),
                ui.zone('body', direction=ui.ZoneDirection.ROW, size='calc(100vh - 70px)', zones=[
                    ui.zone('sidebar', size='350px'),
                    ui.zone('content', direction=ui.ZoneDirection.ROW, zones=[
                        ui.zone('all'),
                        ui.zone('diff')
                    ])
                ])
            ]
        ),
    ])
    q.page['header'] = ui.header_card(box='header', title='Hotel Reviews', subtitle='Explains the hotel reviews', icon='ReviewSolid', icon_color='#00A8E0')
    q.client.review = config.review_column_list[0]

    form_filters = []
    for column in config.filterable_columns:
        choices = [ui.choice(name='empty', label='All')] + [ui.choice(name=str(column), label=str(column)) for column in config.dataset[column].drop_duplicates()]
        form_filters.append(ui.dropdown(name=f'filter_{column}', label=config.column_mapping[column], trigger=True, value='empty', choices=choices))

    sidebar_items = [ui.dropdown(name='review', label='Review type', value=q.client.review, trigger=True,
        choices=[ui.choice(name=column, label=config.column_mapping[column]) for column in config.dataset[config.review_column_list]]
    ),
    ui.separator('Filters')] + form_filters
    q.page['sidebar'] = ui.form_card(box='sidebar', items=sidebar_items)
    q.page['original'] = ui.image_card(box='all', title='Original', type='png', image=plot_word_cloud(config.dataset[q.client.review], q))


def handle_filter(q: Q, key: str, val: str):
    if val == 'empty':
        q.client.filters.pop(key, None)
    else:
        q.client.filters[key] = val


@app('/')
async def serve(q: Q):
    if not q.client.initialized:
        init(q)
        q.client.filters = {}
        q.client.initialized = True

    args = expando_to_dict(q.args)
    for arg in args:
        if str(arg).startswith('filter_'):
            handle_filter(q, str(arg).replace('filter_', ''), q.args[arg])

    sidebar_items = q.page['sidebar'].items
    if q.args.filter_categories:
        # TODO: Remove after https://github.com/h2oai/wave/issues/150 gets resolved.
        sidebar_items[2].dropdown.value = q.args.filter_categories
    if q.args.filter_city:
        # TODO: Remove after https://github.com/h2oai/wave/issues/150 gets resolved.
        sidebar_items[3].dropdown.value = q.args.filter_city
    if q.args.filter_country:
        # TODO: Remove after https://github.com/h2oai/wave/issues/150 gets resolved.
        sidebar_items[4].dropdown.value = q.args.filter_country
    if q.args.filter_postalCode:
        # TODO: Remove after https://github.com/h2oai/wave/issues/150 gets resolved.
        sidebar_items[5].dropdown.value = q.args.filter_postalCode
    if q.args.filter_province:
        # TODO: Remove after https://github.com/h2oai/wave/issues/150 gets resolved.
        sidebar_items[6].dropdown.value = q.args.filter_province
    if q.args.filter_rating:
        # TODO: Remove after https://github.com/h2oai/wave/issues/150 gets resolved.
        sidebar_items[7].dropdown.value = q.args.filter_rating
    if q.args.filter_userCity:
        # TODO: Remove after https://github.com/h2oai/wave/issues/150 gets resolved.
        sidebar_items[8].dropdown.value = q.args.filter_userCity
    if q.args.filter_userProvince:
        # TODO: Remove after https://github.com/h2oai/wave/issues/150 gets resolved.
        sidebar_items[9].dropdown.value = q.args.filter_userProvince
    if q.args.review:
        q.client.review = q.args.review
        # TODO: Remove after https://github.com/h2oai/wave/issues/150 gets resolved.
        sidebar_items[0].dropdown.value = q.client.review
        q.page['original'].image = plot_word_cloud(config.dataset[q.client.review], q)

    if q.client.filters:
        render_diff_word_cloud(q)
    else:
        del q.page['diff']
        # TODO: Remove when https://github.com/h2oai/wave/pull/611 merged.
        q.page['meta'].layouts[0].zones[1].zones[1].zones[1].size = '0'

    await q.page.save()
