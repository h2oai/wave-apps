import pandas as pd

from h2o_wave import Q, app, copy_expando, main, site, ui

page_recommendations = site['/recommendations']


def get_product_mapping() -> dict:
    """
    Mapping of product to department.
    """
    df = pd.read_csv('instacart_products.csv')
    product_names = df.product_name.values
    department_names = df.department.values
    product_mapping = {}

    for i in range(df.shape[0]):
        product_mapping[product_names[i]] = department_names[i]

    product_mapping['No recommendations available'] = 'Please change products in cart'

    return product_mapping


def get_profitability_bucket(profitability: float) -> str:
    """
    Profitability bucket.
    """
    if profitability >= 0.25:
        return "Very High"
    elif profitability >= 0.20:
        return "High"
    elif profitability >= 0.10:
        return "Medium"
    elif profitability >= 0.05:
        return "Low"
    else:
        return "Very Low"


def get_diversity_bucket(diversity: float) -> str:
    """
    Diversity bucket.
    """
    if diversity >= 0.99:
        return "Full"
    elif diversity >= 0.51:
        return "High"
    elif diversity >= 0.49:
        return "Balanced"
    elif diversity > 0.0:
        return "Low"
    else:
        return "None"


def get_diversity_color(diversity: float) -> str:
    """
    Color of diversity stat.
    """
    if diversity in [0.0, 1.0]:
        return 'green'
    else:
        return 'orange'


async def initialize_app(q: Q):
    """
    Initialize app.
    """
    q.client.rulesets = pd.read_csv('instacart_market_basket_model.csv').sort_values('profitability', ascending=False)
    q.client.rulesets.consequents = q.client.rulesets.consequents.apply(lambda x: list(eval(x))[0])
    q.client.product_department = get_product_mapping()
    q.client.product_choices = [ui.choice(name=str(x), label=str(x)) for x, _ in q.client.product_department.items()]
    q.client.df = q.client.rulesets.copy(deep=True)
    q.client.cart_products = ['Banana']
    q.client.suggested_products = ['Organic Hass Avocado', 'Large Lemon', 'Biscoff Cookie']

    q.client.cards_names = [
        page_recommendations.add('rec_1_name', ui.large_stat_card(
            box='1 1 2 1',
            title='',
            value='',
            aux_value='',
            caption=''
        )),
        page_recommendations.add('rec_2_name', ui.large_stat_card(
            box='1 2 2 1',
            title='',
            value='',
            aux_value='',
            caption=''
        )),
        page_recommendations.add('rec_3_name', ui.large_stat_card(
            box='1 3 2 1',
            title='',
            value='',
            aux_value='',
            caption=''
        )),
        page_recommendations.add('rec_4_name', ui.large_stat_card(
            box='1 4 2 1',
            title='',
            value='',
            aux_value='',
            caption=''
        )),
        page_recommendations.add('rec_5_name', ui.large_stat_card(
            box='1 5 2 1',
            title='',
            value='',
            aux_value='',
            caption=''
        ))
    ]

    q.client.cards_profitability = [
        page_recommendations.add('rec_1_profitability', ui.wide_gauge_stat_card(
            box='3 1 2 1',
            title='Profitability',
            value='',
            aux_value='',
            progress=0.0,
            plot_color='blue'
        )),
        page_recommendations.add('rec_2_profitability', ui.wide_gauge_stat_card(
            box='3 2 2 1',
            title='Profitability',
            value='',
            aux_value='',
            progress=0.0,
            plot_color='blue'
        )),
        page_recommendations.add('rec_3_profitability', ui.wide_gauge_stat_card(
            box='3 3 2 1',
            title='Profitability',
            value='',
            aux_value='',
            progress=0.0,
            plot_color='blue'
        )),
        page_recommendations.add('rec_4_profitability', ui.wide_gauge_stat_card(
            box='3 4 2 1',
            title='Profitability',
            value='',
            aux_value='',
            progress=0.0,
            plot_color='blue'
        )),
        page_recommendations.add('rec_5_profitability', ui.wide_gauge_stat_card(
            box='3 5 2 1',
            title='Profitability',
            value='',
            aux_value='',
            progress=0.0,
            plot_color='blue'
        ))
    ]

    q.client.cards_diversity = [
        page_recommendations.add('rec_1_diversity', ui.wide_gauge_stat_card(
            box='5 1 2 1',
            title='Diversity',
            value='',
            aux_value='',
            progress=0.0,
            plot_color='red'
        )),
        page_recommendations.add('rec_2_diversity', ui.wide_gauge_stat_card(
            box='5 2 2 1',
            title='Diversity',
            value='',
            aux_value='',
            progress=0.0,
            plot_color='red'
        )),
        page_recommendations.add('rec_3_diversity', ui.wide_gauge_stat_card(
            box='5 3 2 1',
            title='Diversity',
            value='',
            aux_value='',
            progress=0.0,
            plot_color='red'
        )),
        page_recommendations.add('rec_4_diversity', ui.wide_gauge_stat_card(
            box='5 4 2 1',
            title='Diversity',
            value='',
            aux_value='',
            progress=0.0,
            plot_color='red'
        )),
        page_recommendations.add('rec_5_diversity', ui.wide_gauge_stat_card(
            box='5 5 2 1',
            title='Diversity',
            value='',
            aux_value='',
            progress=0.0,
            plot_color='red'
        ))
    ]

    page_recommendations.save()

    q.page.add('header', ui.header_card(
        box='1 1 9 1',
        title='Shopping Cart Recommendations',
        subtitle='Simulating a recommendation engine',
        icon='ShoppingCartSolid',
        icon_color='$yellow'
    ))

    q.page.add('cart', ui.form_card(
        box='1 2 2 6',
        items=[
            ui.separator('Cart'),
            ui.text('Add products to the cart below and simulate the top recommendations.'),
            ui.picker(
                name='cart_products',
                choices=q.client.product_choices
            ),
            ui.button(name='simulate', label='Simulate', primary=True),
            ui.separator(label='Suggestions'),
            ui.button(name='suggested_product_1', caption='Add to cart', primary=False),
            ui.button(name='suggested_product_2', caption='Add to cart', primary=False),
            ui.button(name='suggested_product_3', caption='Add to cart', primary=False)
        ]
    ))

    q.page.add('recommendations', ui.frame_card(
        box='3 2 7 6',
        title='Recommendations',
        path='/recommendations'
    ))

    await update_cart(q, add_product=False)
    await update_recommendations(q)
    await q.page.save()


async def update_cart(q: Q, add_product: bool = True):
    """
    Update cart.
    """
    if add_product:
        if q.client.suggested_product_1:
            new_product = q.client.suggested_products[0]
        elif q.client.suggested_product_2:
            new_product = q.client.suggested_products[1]
        elif q.client.suggested_product_3:
            new_product = q.client.suggested_products[2]
        else:
            new_product = []

        q.client.cart_products += [new_product]

        q.client.suggested_products = q.client.df[
            q.client.df.antecedents.str.contains(f"'{new_product}'")
        ].consequents.values[:3]

    q.page['cart'].items[2].picker.values = q.client.cart_products

    q.page['cart'].items[5].button.visible = False
    q.page['cart'].items[6].button.visible = False
    q.page['cart'].items[7].button.visible = False

    if len(q.client.suggested_products) > 0:
        q.page['cart'].items[5].button.visible = True
        q.page['cart'].items[5].button.label = q.client.suggested_products[0]

    if len(q.client.suggested_products) > 1:
        q.page['cart'].items[6].button.visible = True
        q.page['cart'].items[6].button.label = q.client.suggested_products[1]

    if len(q.client.suggested_products) > 2:
        q.page['cart'].items[7].button.visible = True
        q.page['cart'].items[7].button.label = q.client.suggested_products[2]

    await q.page.save()


async def update_recommendations(q: Q):
    """
    Update recommendations.
    """
    q.client.df = q.client.rulesets.copy(deep=True)
    q.client.df.antecedents = q.client.df.antecedents.astype(str)

    for product in q.client.cart_products:
        q.client.df = q.client.df[
            q.client.df.antecedents.str.contains(f"'{product}'")
        ]

    q.client.df.drop_duplicates('consequents', inplace=True)

    top_products = q.client.df.consequents.values[:5]
    profitabilities = q.client.df.profitability.values[:5] / 100
    diversities = q.client.df.diversity.values[:5] / 100

    if len(top_products) < 5:
        profitabilities = list(profitabilities) + [0.0] * (5 - len(top_products))
        diversities = list(diversities) + [0.0] * (5 - len(top_products))
        top_products = list(top_products) + ['No recommendations available'] * (5 - len(top_products))

    for i in range(5):
        q.client.cards_names[i].title = top_products[i]
        q.client.cards_names[i].caption = q.client.product_department[top_products[i]]
        q.client.cards_profitability[i].progress = float(profitabilities[i])
        q.client.cards_profitability[i].aux_value = get_profitability_bucket(profitabilities[i])
        q.client.cards_diversity[i].progress = float(diversities[i])
        q.client.cards_diversity[i].aux_value = get_diversity_bucket(diversities[i])
        q.client.cards_diversity[i].plot_color = get_diversity_color(diversities[i])

    page_recommendations.save()


@app('/')
async def serve(q: Q):
    """
    Main serving function.
    """
    if not q.client.initialized:
        await initialize_app(q)
        q.client.initialized = True

    if q.args.suggested_product_1 or q.args.suggested_product_2 or q.args.suggested_product_3:
        copy_expando(q.args, q.client)
        await update_cart(q, add_product=True)
    elif q.args.simulate:
        copy_expando(q.args, q.client)
        if len(q.client.cart_products) == 0:
            q.client.cart_products = ['None']
        await update_recommendations(q)
