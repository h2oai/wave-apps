import h2o  # Use at least 3.32.0.1 for AutoExplain
from h2o.estimators.gbm import H2OGradientBoostingEstimator

import matplotlib.pyplot as plt
import numpy as np
import os
import uuid
import io
import base64


class ChurnPredictor:
    def __init__(self):
        self.gbm = None
        self.train_df = None
        self.predicted_df = None
        h2o.init()

    def build_model(self, training_data_path):
        train_df = h2o.import_file(path=training_data_path, destination_frame='telco_churn_train.csv')

        predictors = train_df.columns
        response = "Churn"
        train, valid = train_df.split_frame([0.8])

        self.gbm = H2OGradientBoostingEstimator(model_id="telco_churn_model", seed=1234)
        self.gbm.train(x=predictors, y=response, training_frame=train, validation_frame=valid)

    def predict(self, testing_data_path=None):
        test_df = self.train_df

        if testing_data_path:
            test_df = h2o.import_file(path=testing_data_path, destination_frame='telco_churn_test.csv')

        self.predicted_df = self.gbm.predict(test_df)

    def get_shap_explanation(self, customer_no):
        pass
