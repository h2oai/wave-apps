from .predictor import Predictor


class Configuration:
    """
    Configuration file for Credit Card Risk app
    """

    def __init__(self):
        self.title = "Credit Card Risk"
        self.subtitle = "Prediction on customer ability to pay credit card bills"
        self.icon = "PaymentCard"
        self.icon_color = "Maroon"

        self.default_model = "credit_risk_model"

        self.id_column = "ID"
        self.y_col = "default.payment.next.month"

        self.training_data_url = "./data/Kaggle/CreditCard-train.csv"
        self.testing_data_url = "./data/Kaggle/CreditCard-train.csv"

        self.figure_config = {"scrollZoom": False, "displayModeBar": None}
        self.approval_threshold = 0.35  # This prediction threshold could be optimized per model but it is hard coded for this example.


config = Configuration()

# Initialize H2O-3 and run ML analysis
predictor = Predictor()
predictor.build_model(config.training_data_url, config.default_model)
predictor.set_testing_data_frame(config.testing_data_url)
predictor.predict()
