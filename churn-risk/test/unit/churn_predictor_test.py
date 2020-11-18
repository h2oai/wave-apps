from decimal import Decimal

import pytest
from src.churn_predictor import ChurnPredictor

import pandas as pd

churn_predictor = ChurnPredictor()
training_data_path = 'data/churnTrain.csv'
pytest.df = pd.read_csv('data/churnTest.csv')
id_column = "Phone_No"


def test_churn_predictor_init():
    assert isinstance(churn_predictor, ChurnPredictor)
    assert churn_predictor.gbm == None
    assert churn_predictor.gbm == None


def test_churn_predictor_get_churn_rate():
    cust_phone_no = 4034933
    churn_predictor.build_model(training_data_path)
    churn_predictor.set_testing_data_frame(training_data_path)
    churn_predictor.predict()
    assert churn_predictor != None
    selected_customer_index = int(pytest.df[pytest.df[id_column] == cust_phone_no].index[0])
    churn_rate = churn_predictor.get_churn_rate_of_customer(selected_customer_index);
    assert churn_rate != None
    assert abs(Decimal(str(churn_rate)).as_tuple().exponent) > 0


def test_get_shap_explanation():
    cust_phone_no = 4034933
    churn_predictor.build_model(training_data_path)
    churn_predictor.set_testing_data_frame(training_data_path)
    churn_predictor.predict()
    selected_customer_index = int(pytest.df[pytest.df[id_column] == cust_phone_no].index[0])
    shap_explanation = churn_predictor.get_shap_explanation(selected_customer_index)
    assert shap_explanation != None
