import pandas as pd

from h2o_wave import Q, app, main, ui

from .config import config
from .utils import get_products_list, get_suggestions, get_trending_products


def init_ui(q: Q):
    q.page.drop()
    q.page['meta'] = ui.meta_card(box='', layouts=[
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


def init_data(q: Q):
    q.client.cart_products = []  # Products in the initial cart

    q.client.rule_set = pd.read_csv(config.rule_set).sort_values('profitability', ascending=False)
    q.client.rule_set.consequents = q.client.rule_set.consequents.apply(lambda x: list(eval(x))[0])


def render_cart(q: Q):
    q.page['cart'] = ui.form_card(
        box='cart',
        items=[
            ui.separator('Cart'),
            ui.text('Search and add products to the cart'),
            ui.picker(
                name='cart_products_picker',
                choices=[ui.choice(name=str(x), label=str(x)) for x in get_products_list()],
                values=q.client.cart_products,
                trigger=True,
            ),
        ]
    )


def render_suggestions(q: Q):
    suggestions = get_suggestions(q.client.rule_set, q.client.cart_products)

    q.page['suggestions'] = ui.form_card(
        box='suggestions',
        items=[
            ui.separator(label='Recommended for You'),
            *[
                ui.button(name='suggestion_btn', label=suggestion, value=suggestion, caption='Add to cart')
                for suggestion in suggestions
            ],
        ]
    )


def render_trending(q: Q):
    trending_products = get_trending_products(q.client.rule_set, q.client.cart_products)

    q.page['trending'] = ui.form_card(
        box='trending',
        items=[
            ui.separator(label='Trending Now'),
            *[
                ui.button(name='trending_btn', label=product, value=product, caption='Add to cart')
                for product in trending_products
            ],
        ]
    )


def handle_cart_products_change(q: Q):
    q.client.cart_products = q.args.cart_products_picker


def handle_suggestion_click(q: Q):
    q.client.cart_products.append(q.args.suggestion_btn)


def handle_trending_click(q: Q):
    q.client.cart_products.append(q.args.trending_btn)


@app('/')
async def serve(q: Q):
    if not q.client.initialized:
        init_data(q)
        q.client.initialized = True

    if q.args.cart_products_picker is not None:
        handle_cart_products_change(q)

    if q.args.suggestion_btn:
        handle_suggestion_click(q)

    if q.args.trending_btn:
        handle_trending_click(q)

    init_ui(q)
    render_cart(q)
    render_suggestions(q)
    render_trending(q)

    await q.page.save()
