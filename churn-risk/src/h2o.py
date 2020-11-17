from h2o_wave import Q, ui, app, main

import h2o  # Use at least 3.32.0.1 for AutoExplain
from h2o.estimators.gbm import H2OGradientBoostingEstimator

import matplotlib.pyplot as plt
import numpy as np
import os
import uuid
import io
import base64

# from h2o.explanation import shap_explain_row_plot, explain_row

@app("/h2o")
async def serve(q: Q):
    h2o.init()

    churn_train = h2o.import_file('/Users/datapattu-mbp16/IdeaProjects/wave-churn-risk/data/churnTrain.csv',
                                  destination_frame='telco_churn_train.csv')

    churn_test = h2o.import_file('/Users/datapattu-mbp16/IdeaProjects/wave-churn-risk/data/churnTest.csv',
                                 destination_frame='telco_churn_test.csv')

    predictors = churn_train.columns
    response = "Churn"

    train, valid = churn_train.split_frame([0.8])

    gbm = H2OGradientBoostingEstimator(model_id="telco_churn_model", seed=1234)
    gbm.train(x=predictors, y=response, training_frame=train, validation_frame=valid)

    # shap_explain_row_plot(gbm, churn_train, row_index=0)
    # explain_row(gbm, churn_train, row_index=0)

    plot = gbm.shap_explain_row_plot(churn_train, row_index=0)
    # gbm.explain_row(churn_train, row_index=0)

    prediction = gbm.predict(churn_test)
    contributions = gbm.predict_contributions(churn_test)

    prediction.get_frame_data()

    # print(churn_test.merge(prediction))

    # prediction.summary()
    # prediction
    # print(prediction.head(rows=100))

    # print(prediction.loc['1']['predict'])

    # prediction.describe()
    # print(prediction[1:2, :])

    # print(contributions)

    h2o.export_file(contributions, "/Users/datapattu-mbp16/IdeaProjects/wave-churn-risk/data/out.csv")

    # Render plot
    # n = 10
    # plt.figure(figsize=(2, 2))
    # plt.scatter(
    #     np.random.rand(n), np.random.rand(n),
    #     s=(30 * np.random.rand(n)) ** 2,
    #     c=np.random.rand(n),
    #     alpha=q.client.alpha / 100.0
    # )
    image_filename = f'{str(uuid.uuid4())}.png'
    plot.savefig(image_filename)

    # Upload
    image_path, = await q.site.upload([image_filename])

    # Clean up
    os.remove(image_filename)

    # Display our plot in our markdown card
    # q.page['plot'] = ui.markdown_card(box='1 1 -1 -1', title='Your plot!', content=f'![plot]({image_path})')

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image = base64.b64encode(buf.read()).decode('utf-8')

    q.page['plot'] = ui.image_card(
        box='1 1 3 5',
        title='An image',
        type='png',
        image=image,
    )

    # Save page
    await q.page.save()
