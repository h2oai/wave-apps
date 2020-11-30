import pandas as pd

from h2o_wave import Q, app, copy_expando, main, ui

from .config import config


def get_product_mapping() -> dict:
    """
    Mapping of product to department.
    """
    df = pd.read_csv('data/instacart_products.csv')
    product_names = df.product_name.values
    department_names = df.department.values
    product_mapping = {}

    for i in range(df.shape[0]):
        product_mapping[product_names[i]] = department_names[i]

    product_mapping['No recommendations available'] = 'Please change products in cart'

    return product_mapping


async def initialize_app(q: Q):
    q.client.rulesets = pd.read_csv('data/instacart_market_basket_model.csv').sort_values('profitability',
                                                                                          ascending=False)
    q.client.rulesets.consequents = q.client.rulesets.consequents.apply(lambda x: list(eval(x))[0])
    q.client.product_department = get_product_mapping()
    q.client.product_choices = [ui.choice(name=str(x), label=str(x)) for x, _ in q.client.product_department.items()]
    q.client.df = q.client.rulesets.copy(deep=True)
    q.client.cart_products = ['Banana']
    q.client.suggested_products = ['Organic Hass Avocado', 'Large Lemon', 'Biscoff Cookie']

    q.page.add('header', ui.header_card(
        box=config.boxes['banner'],
        title=config.title,
        subtitle=config.subtitle,
        icon=config.icon,
        icon_color=config.icon_color,
    ))


def get_suggestions(q: Q, cart_products, count=3):
    df = q.client.df
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
                name='cart_products',
                choices=q.client.product_choices,
                values=get_cart_products(q)
            ),
            ui.button(name='update_cart', label='Update', primary=True),
        ]
    )


def get_cart_products(q: Q):
    return q.args.cart_products or ['Banana']


def render_suggestions(q: Q):
    suggestions = get_suggestions(q, get_cart_products(q))

    q.page['suggestions'] = ui.form_card(
        box=config.boxes['suggestions'],
        items=[
            ui.separator(label='Suggestions'),
            *[
                ui.button(name=suggestion, label=suggestion, caption='Add to cart', primary=False)
                for suggestion in suggestions
            ],
        ]
    )


@app('/')
async def serve(q: Q):
    if not q.client.initialized:
        await initialize_app(q)
        q.client.initialized = True

    print(q.args.cart_products)
    render_cart(q)
    render_suggestions(q)

    await q.page.save()
