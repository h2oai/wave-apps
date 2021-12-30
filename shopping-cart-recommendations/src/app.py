import pandas as pd

from h2o_wave import Q, app, main, ui

from .config import config
from .utils import get_products_list, get_suggestions, get_trending_products


def init_ui(q: Q):
    q.page['meta'] = ui.meta_card(title='Shopping Cart Recomendations', box='', layouts=[
        ui.layout(
            breakpoint='xs',
            zones=[
                ui.zone('header', size='80px'),
                ui.zone('cart', size='250px'),
                ui.zone('trending'),
                ui.zone('suggestions'),
            ]
        ),
        ui.layout(
            breakpoint='m',
            zones=[
                ui.zone('header', size='80px'),
                ui.zone('body', size='1000px', direction=ui.ZoneDirection.ROW, zones=[
                    ui.zone('cart', size='300px'),
                    ui.zone('right-pane', direction=ui.ZoneDirection.COLUMN, zones=[
                        ui.zone('trending', size='600px'),
                        ui.zone('suggestions'),
                    ]),
                ]),
            ]
        ),
        ui.layout(
            breakpoint='xl',
            width='1600px',
            zones=[
                ui.zone('header', size='80px'),
                ui.zone('body', size='750px', direction=ui.ZoneDirection.ROW, zones=[
                    ui.zone('cart', size='300px'),
                    ui.zone('trending'),
                    ui.zone('suggestions'),
                ])
            ]
        )
    ])

    q.page.add('header', ui.header_card(
        box='header',
        title=config.title,
        subtitle=config.subtitle,
        icon=config.icon,
        icon_color=config.icon_color,
    ))

    q.page['suggestions'] = ui.form_card(box='suggestions', items=[])
    q.page['trending'] = ui.form_card(box='trending', items=[])
    q.page['cart'] = ui.form_card(
        box='cart',
        items=[
            ui.separator('Cart'),
            ui.text('Search and add products to the cart'),
            ui.picker(
                name='cart_products',
                choices=[ui.choice(name=str(x), label=str(x)) for x in get_products_list()],
                values=q.client.cart_products,
                trigger=True,
            ),
            ui.button(name='toggle_theme', label='Toggle Theme', primary=True)
        ]
    )
    q.client.theme = 'default'


def init_data(q: Q):
    q.client.cart_products = []  # Products in the initial cart

    q.client.rule_set = pd.read_csv(config.rule_set).sort_values('profitability', ascending=False)
    q.client.rule_set.consequents = q.client.rule_set.consequents.apply(lambda x: list(eval(x))[0])


def update_cart(q: Q):
    q.page['cart'].items[2].picker.values = q.client.cart_products


def render_suggestions(q: Q):
    suggestions = get_suggestions(q.client.rule_set, q.client.cart_products)

    q.page['suggestions'].items = [
        ui.separator(label='Recommended for You'),
        *[
            ui.button(name='suggestion_btn', label=suggestion, value=suggestion, caption='Add to cart')
            for suggestion in suggestions
        ],
    ]


def render_trending(q: Q):
    trending_products = get_trending_products(q.client.rule_set, q.client.cart_products)

    q.page['trending'].items = [
        ui.separator(label='Trending Now'),
        *[
            ui.button(name='trending_btn', label=product, value=product, caption='Add to cart')
            for product in trending_products
        ],
    ]


@app('/')
async def serve(q: Q):
    if not q.client.initialized:
        init_data(q)
        init_ui(q)
        q.client.initialized = True

    if q.args.cart_products is not None:
        q.client.cart_products = q.args.cart_products

    if q.args.suggestion_btn:
        q.client.cart_products.append(q.args.suggestion_btn)

    if q.args.trending_btn:
        q.client.cart_products.append(q.args.trending_btn)

    update_cart(q)
    render_suggestions(q)
    render_trending(q)

    meta = q.page['meta']
    if q.args.toggle_theme:
        meta.theme = q.client.theme = 'h2o-dark' if q.client.theme == 'default' else 'default'

    await q.page.save()
