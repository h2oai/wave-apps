import pandas as pd

from h2o_wave import Q, app, main, ui

from .config import config


def get_product_mapping() -> dict:
    df = pd.read_csv(config.product_mappings)
    product_names = df.product_name.values
    department_names = df.department.values
    product_mapping = {}

    for i in range(df.shape[0]):
        product_mapping[product_names[i]] = department_names[i]

    product_mapping['No recommendations available'] = 'Please change products in cart'

    return product_mapping


def get_products_list():
    df = pd.read_csv(config.product_mappings)
    return df.product_name.values


async def initialize_app(q: Q):
    q.client.cart_products = []
    q.client.rule_set = pd.read_csv(config.rule_set).sort_values('profitability', ascending=False)
    q.client.rule_set.consequents = q.client.rule_set.consequents.apply(lambda x: list(eval(x))[0])
    q.client.product_choices = [ui.choice(name=str(x), label=str(x)) for x in get_products_list()]

    q.page.add('header', ui.header_card(
        box=config.boxes['banner'],
        title=config.title,
        subtitle=config.subtitle,
        icon=config.icon,
        icon_color=config.icon_color,
    ))

    render_cart(q)
    render_suggestions(q)


def get_suggestions(q: Q, cart_products, count=3):
    df = q.client.rule_set
    results = pd.DataFrame(columns=df.columns)

    for product in cart_products:
        f = df[df.antecedents.str.contains(product)]
        results = results.append(f)

    results.sort_values('profitability', ascending=False)
    return results.consequents.values[:count]


def render_cart(q: Q):
    q.page['cart'] = ui.form_card(
        box=config.boxes['cart'],
        items=[
            ui.separator('Cart'),
            ui.text('Add products to the cart below and simulate the top recommendations.'),
            ui.picker(
                name='cart_products_picker',
                choices=q.client.product_choices,
                values=q.client.cart_products,
                trigger=True,
            ),
        ]
    )


def render_suggestions(q: Q):
    suggestions = get_suggestions(q, q.client.cart_products)

    q.page['suggestions'] = ui.form_card(
        box=config.boxes['suggestions'],
        items=[
            ui.separator(label='Suggestions'),
            *[
                ui.button(name='suggestion_btn', label=suggestion, value=suggestion, caption='Add to cart')
                for suggestion in suggestions
            ],
        ]
    )


def handle_cart_products_change(q: Q):
    q.client.cart_products = q.args.cart_products_picker
    render_suggestions(q)


def handle_suggestion_click(q: Q):
    q.client.cart_products.append(q.args.suggestion_btn)
    render_suggestions(q)


@app('/')
async def serve(q: Q):
    if not q.client.initialized:
        await initialize_app(q)
        q.client.initialized = True

    if q.args.cart_products_picker:
        handle_cart_products_change(q)

    if q.args.suggestion_btn:
        handle_suggestion_click(q)

    render_cart(q)

    await q.page.save()
