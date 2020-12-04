class Configuration:
    """
    Configuration file for Explain Ratings
    """

    def __init__(self):
        self.color = "#00A8E0"
        self.image_path = "static/icon.png"
        self.title = "Hotel Reviews"
        self.subtitle = "Explains the hotel reviews"
        self.icon = "ReviewSolid"

        self.review_column_list = ['reviews.title', 'reviews.text']
        self.training_path = "./data/Datafiniti_Hotel_Reviews.csv"
        self.default_model = "explain_rating_model"

        self.boxes = {
            "banner": "1 1 -1 1",
            "content": "1 2 -1 -1",
            "left_panel": "1 2 4 3",
            "new_filter": "1 5 4 1",
            "filters": "1 6 4 -1",
            "middle_panel": "1 5 4 -1",
            "right_panel": "1 9 4 -1",
        }
