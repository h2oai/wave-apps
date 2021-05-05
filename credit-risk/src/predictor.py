import h2o
import pandas as pd

from h2o_wave_ml import build_model, ModelType



class CreditPredictor:
    """
    CreditPredictor builds an abstraction between WaveML library and the Credit Risk app.
    """

    def __init__(self):
        self.model = None
        self.train_df = None
        self.test_df = None
        self.predicted_df = None
        self.contributions_df = None

    def build_model(self, training_data_path, model_id):
        self.wave_model = build_model(
            train_file_path=training_data_path,
            target_column='default.payment.next.month',
            model_type=ModelType.H2O3,
            _h2o3_max_runtime_secs=30,
            _h2o3_nfolds=0,
            _h2o3_include_algos=['DRF', 'XGBoost', 'GBM']
        )

        self.model = self.wave_model.model

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
