from .predictor import Predictor


class Configuration:
    """
    Configuration file for Credit Card Risk app
    """

    def __init__(self):
        self.color = "Maroon"
        self.total_gauge_color = "#FF0102"
        self.image_path = "static/icon.png"

        self.default_model = "credit_risk_model"

        self.id_column = "ID"
        self.y_col = "default.payment.next.month"

        self.title = "Credit Card Risk"
        self.subtitle = "Prediction on customer ability to pay credit card bills"
        self.icon = "PaymentCard"

        self.training_data_url = "./data/Kaggle/CreditCard-train.csv"
        self.testing_data_url = "./data/Kaggle/CreditCard-train.csv"

        self.boxes = {
            "banner": "1 1 3 1",
            "content": "1 2 -1 -1",
            "logo": "11 1 -1 1",
            "navbar": "4 1 -1 1",
            "customer": "1 2 2 1",
            "churn_rate": "1 3 2 1",
            "stat_pie": "8 2 -1 2",
            "shap_plot": "3 2 -1 9",
            "top_negative_pd_plot": "1 15 -1 11",
            "top_positive_pd_plot": "1 26 -1 11",
            "risk_table": "1 2 -1 7",
            "risk_table_selected": "1 2 2 14",
            "button_group": "1 16 -1 1",
            "risk_explanation": "3 11 -1 5",
        }

        self.figure_config = {"scrollZoom": False, "displayModeBar": None}
        self.approval_threshold = 0.35


config = Configuration()
predictor = Predictor()
