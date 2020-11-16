import h2o  # Use at least 3.32.0.1 for AutoExplain
from h2o.estimators.gbm import H2OGradientBoostingEstimator


class ChurnPredictor:
    def __init__(self):
        self.gbm = None
        self.train_df = None
        self.test_df = None
        self.predicted_df = None
        self.contributions_df = None

        h2o.init()

    def build_model(self, training_data_path):
        train_df = h2o.import_file(path=training_data_path, destination_frame='telco_churn_train.csv')

        predictors = train_df.columns
        response = "Churn?"
        train, valid = train_df.split_frame([0.8])

        self.gbm = H2OGradientBoostingEstimator(model_id="telco_churn_model", seed=1234)
        self.gbm.train(x=predictors, y=response, training_frame=train, validation_frame=valid)

    def set_testing_data_frame(self, testing_data_path):
        self.test_df = h2o.import_file(path=testing_data_path, destination_frame='telco_churn_test.csv')

    def predict(self):
        self.predicted_df = self.gbm.predict(self.test_df)
        self.contributions_df = self.gbm.predict_contributions(self.test_df)

    def get_churn_rate_of_customer(self, row_index):
        return round(float(self.predicted_df.as_data_frame()['TRUE'][row_index]) * 100, 2)

    def get_shap_explanation(self, row_index):
        return self.gbm.shap_explain_row_plot(frame=self.test_df, row_index=row_index)

    def get_top_negative_pd_explanation(self, row_index):
        column_index = self.contributions_df.idxmin(axis=1).as_data_frame()['which.min'][row_index]
        return self.gbm.pd_plot(frame=self.test_df, row_index=row_index, column=self.test_df.col_names[column_index])

    def get_top_positive_pd_explanation(self, row_index):
        column_index = self.contributions_df.idxmax(axis=1).as_data_frame()['which.max'][row_index]
        return self.gbm.pd_plot(frame=self.test_df, row_index=row_index, column=self.test_df.col_names[column_index])