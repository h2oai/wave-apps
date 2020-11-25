import h2o
import pandas as pd

from h2o.estimators.gbm import H2OGradientBoostingEstimator


class Predictor:
    """
    Wrapper for H2O-3

    ChurnPredictor builds an abstraction between H2O-3 machine learning library and the Churn Risk app
    giving the developer freedom to integrate any 3rd party machine library with a minimal change to the app code.
    """

    def __init__(self):
        self.model = None
        self.train_df = None
        self.test_df = None
        self.predicted_df = None
        self.contributions_df = None

        h2o.init()

    def build_model(self, training_data_path, model_id):
        train_df = h2o.import_file(path=training_data_path)

        predictors = train_df.columns
        response = "default.payment.next.month"
        train, valid = train_df.split_frame([0.8])

        self.model = H2OGradientBoostingEstimator(model_id=model_id, seed=100)
        self.model.train(
            x=predictors, y=response, training_frame=train, validation_frame=valid
        )

    def set_testing_data_frame(self, testing_data_path):
        self.test_df = h2o.import_file(path=testing_data_path)

    def get_testing_data_as_pd_frame(self):
        return pd.DataFrame(self.test_df.as_data_frame())

    def get_predict_data_as_pd_frame(self):
        return pd.DataFrame(self.predicted_df.as_data_frame())

    def predict(self):
        self.predicted_df = self.model.predict(self.test_df)
        self.contributions_df = self.model.predict_contributions(self.test_df)

    def get_churn_rate_of_customer(self, row_index):
        """
        Return the churn rate of given customer as a percentage.

        :param row_index: row index of the customer in dataframe
        :return: percentage as a float
        """
        return round(
            float(self.predicted_df.as_data_frame()["TRUE"][row_index]) * 100, 2
        )

    def get_shap_explanation(self, row_index):
        return self.model.shap_explain_row_plot(frame=self.test_df, row_index=row_index)

    def get_top_negative_pd_explanation(self, row_index):
        """
        Return the partial dependence explanation of the top negatively contributing feature.

        :param row_index: row index to select from H2OFrame for the explanation
        :return: matplotlib figure object
        """
        column_index = self.contributions_df.idxmin(axis=1).as_data_frame()[
            "which.min"
        ][row_index]
        return self.model.pd_plot(
            frame=self.test_df,
            row_index=row_index,
            column=self.test_df.col_names[column_index],
        )

    def get_top_positive_pd_explanation(self, row_index):
        """
        Return the partial dependence explanation of the top positively contributing feature.

        :param row_index: row index to select from H2OFrame for the explanation
        :return: matplotlib figure object
        """
        column_index = self.contributions_df.idxmax(axis=1).as_data_frame()[
            "which.max"
        ][row_index]
        return self.model.pd_plot(
            frame=self.test_df,
            row_index=row_index,
            column=self.test_df.col_names[column_index],
        )
