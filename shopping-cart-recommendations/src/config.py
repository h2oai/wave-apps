class Configuration:
    """
    Configuration file for Credit Card Risk app
    """

    def __init__(self):
        self.title = "Shopping Cart Recommendations"
        self.subtitle = "Recommendations based on shopping cart items"
        self.icon = "ShoppingCartSolid"
        self.icon_color = "$yellow"

        self.rule_set = 'data/instacart_market_basket_model.csv'
        self.product_mappings = 'data/instacart_products.csv'

        self.boxes = {
            'banner': '1 1 -1 1',
            'cart': '1 2 2 9',
            'suggestions': '3 2 10 9',
        }


config = Configuration()
