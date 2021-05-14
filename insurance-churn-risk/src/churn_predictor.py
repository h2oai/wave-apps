import h2o
from typing import List, Optional, Tuple, Any, Union

from h2o_wave_ml import build_model, ModelType


class ChurnPredictor:
    """
    ChurnPredictor builds an abstraction between WaveML library and the Insurance Churn Risk app.
    """

    def __init__(
        self,
        train_dataset_path: str,
        test_dataset_path: str,
        target_column: str,
        categorical_columns: Optional[List[str]] = None,
        drop_columns: Optional[List[str]] = None
    ):
        self.wave_model = build_model(
            train_file_path=train_dataset_path,
            target_column=target_column,
            model_type=ModelType.H2O3,
            categorical_columns=categorical_columns,
            drop_columns=drop_columns,
            _h2o3_max_runtime_secs=30,
            _h2o3_nfolds=0,
            _h2o3_include_algos=['DRF', 'GBM']
        )

        self.model = self.wave_model.model

        self.test_df = h2o.import_file(path=test_dataset_path)
        for column in categorical_columns:
            self.test_df[column] = self.test_df[column].asfactor()

        self.churn_probabilities = self.model.predict(self.test_df)[:,-1].as_data_frame().values
        self.contributions_df = self.model.predict_contributions(self.test_df).drop('BiasTerm').as_data_frame()

    def get_churn_rate(self, row_index: Optional[int]) -> float:
        churn = self.churn_probabilities[row_index] if row_index is not None else self.churn_probabilities.mean(axis=0)
        return round(float(churn) * 100, 2)

    def get_shap(self, row_index: Optional[int]) -> List[Tuple[Any, Any]]:
        np_row = self.contributions_df.mean(axis=0) if row_index is None else self.contributions_df.iloc[row_index]
        np_row = np_row.to_numpy()
        shap = [(self.contributions_df.columns[i], np_row[i]) for i in range(len(self.contributions_df.columns))]
        shap.sort(key=lambda e : e[1])
        return shap

    def get_negative_explanation(self, row_index: Optional[int], min_contrib_col: Optional[str]) -> Tuple[bool, Any, List]:
        contribs = min_contrib_col or self.contributions_df.idxmin(axis=1)[row_index]
        return self._get_explanation(contribs, row_index)

    def get_positive_explanation(self, row_index: Optional[int], max_contrib_col: Optional[str]) -> Tuple[bool, Any, List]:
        contribs = max_contrib_col or  self.contributions_df.idxmax(axis=1)[row_index]
        return self._get_explanation(contribs, row_index)

    @staticmethod
    def get_python_type(val) -> Union[str, float, int]:
        return val if isinstance(val, (str, float, int)) else val.item()

    @classmethod
    def _get_size(cls, group_size, idx: int) -> Union[str, float, int]:
        return 0 if idx > len(group_size) - 1 else cls.get_python_type(group_size[idx])

    def _get_explanation(self, contrib, row_index: Optional[int]) -> Tuple[bool, Any, List]:
        contrib_col = self.test_df[contrib]
        partial_plot = self.model.partial_plot(
            self.test_df,
            plot=False,
            cols=[contrib],
            nbins=contrib_col.nlevels()[0] + 1 if contrib_col.isfactor()[0] else 20,
            row_index=row_index
        )[0].as_data_frame()

        if self.test_df.type(contrib) in ['int', 'real']:
            bins = [contrib_col.na_omit().min()] + partial_plot.iloc[:, 0].tolist() + [contrib_col.na_omit().max()]

            group_by_size = contrib_col.cut(
                bins,
                labels=[str(i) for i in bins[1:]],
                include_lowest=True
            ).table().as_data_frame().iloc[:, 1].values

        else:
            group_by_size = contrib_col.as_data_frame().groupby(contrib).size().values

        rows = [(
            partial_plot.iloc[i, 0],
            partial_plot.iloc[i, 1],
            self._get_size(group_by_size, i)
        ) for i in range(len(partial_plot))]

        return isinstance(partial_plot.iloc[0: 0], float), contrib, rows
