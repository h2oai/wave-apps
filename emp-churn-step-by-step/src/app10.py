# Step 10
# Refresh only relevant components. Stop re-creating cards - just refresh attributes
# ---
from h2o_wave import main, app, Q, ui, on, handle_on, data

import altair
import numpy as np
import pandas as pd
from typing import List

import logging
from os import environ
import traceback

log = logging.getLogger("app")

def setup_logger():
    """
    Default Logging Level is INFO. To overwrite set environment variable LOG_LEVEL
    Available options: INFO, DEBUG, ....
    :return:
    """
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s - [%(name)s] - %(levelname)s - %(message)s"
    )
    ch.setFormatter(formatter)
    log.addHandler(ch)
    log.setLevel(environ.get("LOG_LEVEL", "INFO").upper())


def on_startup():
    """
    Initializer logger
    :return:
    """
    setup_logger()
    log.info('+++++++App started!++++++++++')


@app('/', on_startup=on_startup, mode='unicast')
async def serve(q: Q):
    try:
        # log.info - always printed
        log.info("====== Start serve Function ========")
        log.info(f"q.args: {q.args}")
        # log.info(f"q.client: {q.client}")

        # log.debug - printed only when LOG_LEVEL is set to DEBUG
        log.debug(f"q.user: {q.user}")
        log.debug(f"q.events: {q.events}")

        # First time the app is loaded
        if not q.app.initialized:
            await init_app(q)
            q.app.initialized = True

        # First time a browser(tab) opens the app
        if not q.client.initialized:
            await init(q)
            q.client.initialized = True
            await q.page.save()
        else:
            action_taken = False
            if q.args.threshold is not None and q.client.threshold != q.args.threshold:
                q.client.threshold = q.args.threshold
                await render_threshold(q)
                action_taken = True

            if q.args.render_employee is not None and len(q.args.render_employee) == 1 and int(
                    q.args.render_employee[0]) != q.client.employee_num:
                q.client.employee_num = int(q.args.render_employee[0])
                await render_emp_shapley(q)
                action_taken = True

            if not action_taken:
                '''We should never get here, unless user did not change anything'''
                log.info("++++++++Unhandled condition or no Change+++++++++++++")
                '''Will result in loading spinner going away '''
                q.page['non-existent'].items = []

        await q.page.save()
        log.info("====== End serve Function ========")

    # In the case of an exception, handle and report it to the log/stdout
    except Exception as err:
        log.error(f"Unhandled Application Error: {str(err)}")
        log.error(traceback.format_exc())
        raise Exception(f"Unhandled Application Error: : {err}")


async def init_app(q: Q) -> None:
    # Read and load data into memory
    log.info("==Start init_app Function ==")
    q.app.predictions = pd.read_csv("./src/static/predictions.csv")
    q.app.predictions = q.app.predictions.rename(columns={'Attrition.Yes': "Prediction"})
    q.app.shapley = pd.read_csv("./src/static/shapley_values.csv")
    log.info("==Complete init_app Function ==")


async def init(q: Q) -> None:
    log.info("==Start init Function ==")
    q.client.cards = set()
    q.client.dark_mode = False
    q.client.initialized = False

    q.page['meta'] = ui.meta_card(
        box='',
        title='Employee Churn Prediction',
        layouts=[
            ui.layout(
                breakpoint='xs',
                min_height='100vh',
                max_width='1200px',
                zones=[
                    ui.zone('header'),
                    ui.zone('content', size='1', zones=[
                        ui.zone('horizontal', direction=ui.ZoneDirection.ROW),
                        ui.zone('vertical', size='1', )
                    ]),
                    ui.zone(name='footer'),
                ]
            )
        ]
    )
    q.page['header'] = ui.header_card(
        box='header',
        title='Employee Churn Prediction',
        subtitle="Predict which employees are at risk and identify relevant factors."
    )
    q.page['footer'] = ui.footer_card(
        box='footer',
        caption='Made with 💛 using [H2O Wave](https://wave.h2o.ai).'
    )

    spec = altair.Chart(q.app.predictions).mark_bar() \
        .encode(altair.X("Prediction", bin=True), y='count()', ) \
        .properties(width='container', height='container') \
        .interactive() \
        .to_json()

    add_card(q, 'predictions_card', ui.vega_card(box='horizontal', title='Churn Predictions',
                                                 specification=spec
                                                 ))

    # Variable importance graph. Get List of columns and importance
    varimp, q.client.varimp_col = get_varimp(q.app.shapley)

    add_card(q, 'varimp_card', ui.plot_card(box='horizontal',
                                            title='Top Factors Affecting Churn',
                                            data=data('feature importance', 5, rows=varimp),
                                            plot=ui.plot([ui.mark(type='interval', x='=importance', y='=feature',
                                                                  x_min=0, color='#9c3a3a')])
                                            ))

    # Card with threshold slider description
    add_card(q, 'description_card', ui.form_card(box='vertical', items=[
        ui.text("Use the slider below to change the cutoff for churn prediction and update the statistics.")
    ]
                                                 ))

    q.client.threshold = 0.5
    add_card(q, 'threshold_card', ui.form_card(box='vertical', items=[ui.slider(name='threshold',
                                                                                label='Prediction Threshold',
                                                                                min=0,
                                                                                max=0.9,
                                                                                step=0.1,
                                                                                value=q.client.threshold,
                                                                                trigger=True,
                                                                                )]))

    q.client.churned_employees = churned_employees = q.app.predictions[
        q.app.predictions['Prediction'] > q.client.threshold]

    # Stats Cards
    add_card(q, 'stats_card', ui.form_card(box='vertical', items=[
        ui.stats([
            ui.stat(label='Number of Employees',
                    value=str(len(churned_employees)),
                    caption='Predicted Churn Employees'),
            ui.stat(label='% of Employees',
                    value="{0:.0%}".format(len(churned_employees) / len(q.app.predictions)),
                    caption='Predicted Churn Employees'),
            ui.stat(label='Average Years at the Company', value=str(round(churned_employees.YearsAtCompany.mean())),
                    caption='Predicted Churn Employees'),
        ], justify='between')]))

    # Churned Employees Table
    cols = ['EmployeeNumber'] + q.client.varimp_col + ["Prediction"]
    add_card(q, 'table_card', ui.form_card(box='vertical', items=[
        ui.table(
            name='render_employee',
            columns=[ui.table_column(name=i, label=i, sortable=True) for i in cols],
            rows=[ui.table_row(name=str(row['EmployeeNumber']),
                               cells=[str(k) for k in row[cols]]) for i, row in churned_employees.iterrows()]
        )]))

    # Display Shapley values for the first employee in the table
    q.client.employee_num = q.client.churned_employees['EmployeeNumber'].iloc[0]
    q.client.employee_varimp = get_local_varimp(q.app.shapley[q.app.shapley['EmployeeNumber'] == q.client.employee_num])
    add_card(q, 'shap_card',
             ui.plot_card(box='vertical',
                          title='Top Factors Affecting Churn for Employee {}'.format(q.client.employee_num),
                          data=data('feature importance color', 5, rows=q.client.employee_varimp),
                          plot=ui.plot([ui.mark(type='interval', x='=importance', y='=feature', color='=color',
                                                color_domain=['decreases risk', 'increases risk'],
                                                color_range='#28733b #9c3a3a')])
                          ))

    log.info("==Complete init Function ==")


async def render_threshold(q:Q):
    '''
    Accept threshold value from slider and Refresh Stats cars and table of employees
    :param q:
    :return:
    '''
    log.info("==Start render_threshold Function ==")

    # Get employees for the given threshold
    q.client.churned_employees = q.app.predictions[q.app.predictions['Prediction'] > q.client.threshold]

    # Update Stats cards
    q.page['stats_card'].items[0].stats.items[0].value = str(9999)
    q.page['stats_card'].items[0].stats.items[0].value = str(len(q.client.churned_employees))
    q.page['stats_card'].items[0].stats.items[1].value = "{0:.0%}".format(len(q.client.churned_employees) / len(q.app.predictions))
    q.page['stats_card'].items[0].stats.items[2].value = str(round(q.client.churned_employees.YearsAtCompany.mean()))

    # Update Churned Employees Table
    cols = ['EmployeeNumber'] + q.client.varimp_col + ["Prediction"]
    q.page['table_card'].items[0].table.rows = [ui.table_row(name=str(row['EmployeeNumber']), cells=[str(k) for k in row[cols]]) for i, row in
            q.client.churned_employees.iterrows()]

    log.info("==Complete render_threshold Function ==")


async def render_emp_shapley(q: Q):
    '''
    Refresh Shapley values for the selected employee.
    :param q:
    :return:
    '''
    log.info("==Start render_emp_shapley Function ==")
    q.client.employee_varimp = get_local_varimp(q.app.shapley[q.app.shapley['EmployeeNumber'] == q.client.employee_num])

    # Refresh Shapley Values Plot
    q.page['shap_card'].title = 'Top Factors Affecting Churn for Employee {}'.format(q.client.employee_num)
    q.page['shap_card'].data = q.client.employee_varimp
    log.info("==Complete render_emp_shapley Function ==")


def get_varimp(shapley_vals, top_n=5):
    '''
    Get Global variable importance based on Shapley Values
    :param shapley_vals:
    :param top_n:
    :return:
    '''
    log.info("==Start get_varimp Function ==")
    varimp = shapley_vals[[i for i in shapley_vals.columns if 'contrib' in i and i != 'contrib_bias']]
    varimp = varimp.abs().mean().reset_index()
    varimp.columns = ["Feature", "Importance"]
    varimp['Feature'] = varimp['Feature'].str.replace("contrib_", "")
    varimp = varimp.sort_values(by="Importance", ascending=False).head(n=top_n)
    varimp = varimp.values.tolist()[::-1]
    varimp_col = [i[0] for i in varimp]
    log.info("==Complete get_varimp Function ==")
    return varimp, varimp_col


def get_local_varimp(shapley_vals, top_n=5):
    '''
    Format Shapley Values for given employee
    :param shapley_vals:
    :param top_n:
    :return:
    '''
    log.info("==Start get_local_varimp Function ==")
    varimp = shapley_vals[[i for i in shapley_vals.columns if 'contrib' in i and i != 'contrib_bias']]
    varimp = varimp.iloc[0].reset_index()
    varimp.columns = ["Feature", "Importance"]
    varimp['Feature'] = varimp['Feature'].str.replace("contrib_", "")
    varimp['Feature'] = ['{}: {}'.format(i, shapley_vals.iloc[0][i]) for i in varimp['Feature']]
    varimp['Color'] = np.where(varimp['Importance'] < 0, 'decreases risk', 'increases risk')
    varimp = varimp.reindex(varimp['Importance'].abs().sort_values(ascending=False).index).head(n=top_n)
    varimp = varimp.values.tolist()[::-1]
    log.info("==Complete get_local_varimp Function ==")

    return varimp


# Use for cards that should be deleted on calling `clear_cards`. Useful for routing and page updates.
def add_card(q, name, card) -> None:
    log.info("==Start add_card Function for card:"+str(name)+" ==")
    q.client.cards.add(name)
    q.page[name] = card
    log.info("==Complete add_card Function==")

# Not in use
def clear_cards(q, ignore=[]) -> None:
    log.info("==Start clear_cards Function==")
    for name in q.client.cards.copy():
        if name not in ignore:
            del q.page[name]
            q.client.cards.remove(name)

    log.info("==Complete clear_cards Function==")