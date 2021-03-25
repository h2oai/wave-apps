import h2o

from h2o.estimators.gbm import H2OGradientBoostingEstimator


class ChurnPredictor:
    """
    Wrapper for H2O-3

    ChurnPredictor builds an abstraction between H2O-3 machine learning library and the Churn Risk app
    giving the developer freedom to integrate any 3rd party machine library with a minimal change to the app code.
    """

    def __init__(self):
        h2o.init()
        # Initialize H2O-3 model and tests data set
        self.train_df = h2o.import_file(path='./data/churnTrain.csv', destination_frame="telco_churn_train.csv")

        train, valid = self.train_df.split_frame([0.8])
        self.model = H2OGradientBoostingEstimator(model_id="telco_churn_model", seed=1234)
        self.model.train(x=self.train_df.columns, y="Churn?", training_frame=train, validation_frame=valid)

        self.h2o_test_df = h2o.import_file(path='./data/churnTest.csv', destination_frame="telco_churn_test.csv")
        self.predicted_df = self.model.predict(self.h2o_test_df).as_data_frame()
        self.contributions_df = self.model.predict_contributions(self.h2o_test_df).drop('BiasTerm').as_data_frame()

    def get_churn_rate(self, row_index: int):
        return round(float(self.predicted_df["TRUE"][row_index]) * 100, 2)

    def get_shap(self, row_index: int):
        np_row = self.contributions_df.iloc[row_index].to_numpy()
        shap= [(self.contributions_df.columns[i], np_row[i]) for i in range(len(self.contributions_df.columns))]
        shap.sort(key=lambda e : e[1])
        return shap 
    
    def get_python_type(self, val):
        return val if isinstance(val, (str, float)) else val.item()
        
    def get_size(self, group_size, idx: int):
        return 0 if idx > len(group_size) - 1 else self.get_python_type(group_size[idx])

    def get_negative_explanation(self, row_index: int):
        min_contrib = self.contributions_df.idxmin(axis=1)[row_index]
        min_contrib_col = self.h2o_test_df[min_contrib]
        partial_plot = self.model.partial_plot(
            self.h2o_test_df, 
            plot=False,
            cols=[min_contrib],
            nbins=min_contrib_col.nlevels()[0] + 1 if min_contrib_col.isfactor()[0] else 20,
            row_index=row_index
        )[0]
        group_by_size = min_contrib_col.as_data_frame().groupby(min_contrib).size().values
        churn_rows = [(partial_plot[0][i], partial_plot[1][i], self.get_size(group_by_size, i)) for i in range(len(partial_plot[0]))]
        return isinstance(partial_plot[0][0], float), min_contrib, churn_rows

    def get_positive_explanation(self, row_index: int):
        max_contrib = self.contributions_df.idxmax(axis=1)[row_index]
        max_contrib_col = self.h2o_test_df[max_contrib]
        partial_plot = self.model.partial_plot(
            self.h2o_test_df,
            plot=False,
            cols=[max_contrib],
            nbins=max_contrib_col.nlevels()[0] + 1 if max_contrib_col.isfactor()[0] else 20,
            row_index=row_index
        )[0]
        group_by_size = max_contrib_col.as_data_frame().groupby(max_contrib).size().values
        retention_rows = [(partial_plot[0][i], partial_plot[1][i], self.get_size(group_by_size, i)) for i in range(len(partial_plot[0]))]
        return isinstance(partial_plot[0][0], float), max_contrib, retention_rows 
