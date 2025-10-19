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
    word_cloud.generate(' '.join(df.astype(str)))

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
    df = config.dataset.copy()

    for key, value in q.client.filters.items():
        df = df[df[key] == value]

    if len(df):
        q.page['diff'] = ui.image_card(
            box='content',
            title='Filtered Reviews',
            type='png',
            image=plot_word_cloud(df[q.client.review], q)
        )
    else:
        q.page['diff'] = ui.form_card(
            box='content',
            items=[ui.message_bar(type='warning', text='No reviews match the current filters!')]
        )


def init(q: Q):
    q.page['meta'] = ui.meta_card(box='', title='Explain Ratings', layouts=[
        ui.layout(
            breakpoint='xs',
            zones=[
                ui.zone('header'),
                ui.zone('body', direction=ui.ZoneDirection.ROW, size='calc(100vh - 70px)', zones=[
                    ui.zone('sidebar', size='350px'),
                    ui.zone('content', direction=ui.ZoneDirection.ROW)
                ])
            ]
        ),
    ])
    q.page['header'] = ui.header_card(
        box='header',
        title='Hotel Reviews',
        subtitle='Explains the hotel reviews',
        icon='ReviewSolid',
        icon_color='#00A8E0',
        items=[
            ui.toggle(name='theme_dark', label='Dark Mode', value=False, trigger=True)
        ]
    )
    q.client.review = config.review_column_list[0]
    q.client.filters = {}

    # Build filter dropdowns dynamically
    form_filters = []
    for column in config.filterable_columns:
        choices = [ui.choice(name='empty', label='All')] + [
            ui.choice(name=str(val), label=str(val)) for val in sorted(config.dataset[column].dropna().unique())
        ]
        form_filters.append(
            ui.dropdown(
                name=f'filter_{column}',
                label=config.column_mapping[column],
                trigger=True,
                value='empty',
                choices=choices
            )
        )

    sidebar_items = [
        ui.dropdown(
            name='review',
            label='Review type',
            value=q.client.review,
            trigger=True,
            choices=[ui.choice(name=col, label=config.column_mapping[col]) for col in config.review_column_list]
        ),
        ui.separator('Filters')
    ] + form_filters

    q.page['sidebar'] = ui.form_card(box='sidebar', items=sidebar_items)
    q.page['original'] = ui.image_card(
        box='content',
        title='All Reviews',
        type='png',
        image=plot_word_cloud(config.dataset[q.client.review], q)
    )
    q.client.initialized = True


def handle_filter(q: Q, key: str, val: str):
    if val == 'empty':
        q.client.filters.pop(key, None)
    else:
        q.client.filters[key] = val


def sync_dropdown_states(q: Q):
    """Sync all dropdowns in sidebar to current client state (workaround for Wave #150)."""
    items = q.page['sidebar'].items
    # Map item name to index for safe updates
    item_map = {}
    for i, item in enumerate(items):
        if hasattr(item, 'dropdown') and item.dropdown.name:
            item_map[item.dropdown.name] = i

    # Sync review type
    if 'review' in item_map:
        items[item_map['review']].dropdown.value = q.client.review

    # Sync filters
    for col in config.filterable_columns:
        dropdown_name = f'filter_{col}'
        if dropdown_name in item_map:
            items[item_map[dropdown_name]].dropdown.value = q.client.filters.get(col, 'empty')


async def update_theme(q: Q):
    q.page['meta'].theme = 'h2o-dark' if q.args.theme_dark else 'light'


@app('/')
async def serve(q: Q):
    if not q.client.initialized:
        init(q)

    # Handle theme toggle
    if q.args.theme_dark is not None:
        await update_theme(q)
        sync_dropdown_states(q)
        await q.page.save()
        return

    # Handle review type change
    if q.args.review is not None:
        q.client.review = q.args.review

    # Handle filter changes
    args = expando_to_dict(q.args)
    for arg, val in args.items():
        if arg.startswith('filter_'):
            col = arg.replace('filter_', '')
            handle_filter(q, col, val)

    # Always sync dropdown states to prevent visual reset (Wave #150 workaround)
    sync_dropdown_states(q)

    # Update visuals
    q.page['original'].image = plot_word_cloud(config.dataset[q.client.review], q)
    if q.client.filters:
        render_diff_word_cloud(q)
    elif 'diff' in q.page:
        del q.page['diff']

    await q.page.save()