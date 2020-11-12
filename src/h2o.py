from h2o_wave import Q, ui, app, main

import h2o  # Use at least 3.32.0.1 for AutoExplain
from h2o.estimators.gbm import H2OGradientBoostingEstimator
# from h2o.explanation import shap_explain_row_plot, explain_row

@app('/h2o')
async def serve(q: Q):
    h2o.init()
    churn_train = h2o.import_file('https://h2o-internal-release.s3-us-west-2.amazonaws.com/data/Splunk/churn.csv',
                                  destination_frame='telco_churn_train.csv')
    churn_train.summary()
    churn_train.head()
    predictors = churn_train.columns
    response = "Churn?"

    gbm = H2OGradientBoostingEstimator(model_id="telco_churn_model", seed=1234)
    gbm.train(x = predictors, y = response, training_frame = churn_train)

    # shap_explain_row_plot(gbm, churn_train, row_index=0)
    # explain_row(gbm, churn_train, row_index=0)

    gbm.shap_explain_row_plot(churn_train, row_index=0)
    gbm.explain_row(churn_train, row_index=0)

    # q.page['h2o'] = ui.form_card(
    #     box="1 1 5 5",
    #     items=items
    # )

    await q.page.save()