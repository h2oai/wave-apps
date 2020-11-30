class Configuration:
    """
    Configuration file for Twitter Sentiment
    """

    def __init__(self):
        self.color = "#00A8E0"
        self.total_gauge_color = "#FF0102"
        self.image_path = "static/icon.jpeg"

        self.default_model = "twitter_sentiment_model"

        self.title = "Twitter Sentiment"
        self.subtitle = "Searches twitter hashtags and sentiment analysis"
        self.icon = "UpgradeAnalysis"

        self.boxes = {
            "banner": "1 1 3 1",
            "logo": "11 1 -1 1",
            "navbar": "4 1 -1 1",
            "search_click": "10 2 -1 1",
            "search_tab": "1 2 9 1"
        }
