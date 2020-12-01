import pandas as pd

from .config import config


def get_products_list():
    df = pd.read_csv(config.product_mappings)
    return df.product_name.values


def get_suggestions(df, cart_products, count=3):
    """
    Get product suggestions based on the products already in the cart.

    :param df: Pandas dataframe of market basket analysis rule set
    :param cart_products: list of products in the cart
    :param count: no of suggestions needed
    :return: list of strings of suggested product names
    """
    suggestions = pd.DataFrame(columns=df.columns)

    for product in cart_products:
        filtered_df = df[df.antecedents.str.contains(product) & is_not_in_cart(cart_products, df.consequents)]
        suggestions = suggestions.append(filtered_df)

    suggestions.sort_values('popularity', ascending=False)
    return suggestions.consequents.values[:count]


def get_trending_products(df, cart_products, count=5):
    """
    Get trending products at the moment. This is not user/order specific.

    :param df: Pandas dataframe of market basket analysis rule set
    :param cart_products: list of products in the cart. This needed to skip same products in the output.
    :param count: no of trending products needed
    :return: list of strings of trending product names
    """
    # TODO: Add a proper logic to get trending products
    df = df[is_not_in_cart(cart_products, df.antecedents)]
    df.sort_values('profitability', ascending=False)
    return df.antecedents.values[:count]


def is_not_in_cart(cart_products, suggestions):
    """
    Check if suggested product is already in the cart.

    :param cart_products: list of products in the cart
    :param suggestions: Pandas series of product suggestions
    :return: Pandas series of booleans with same index as suggestions
    """
    return [suggestion not in cart_products for suggestion in suggestions]
