# Step 13
# Add tabs and tabs switching
# Set H2O_WAVE_NO_LOG=1 to avoid printing server (waved) messages
# ---
from h2o_wave import main, app, Q, ui, on, data
from h2o_wave.core import expando_to_dict
from typing import Optional, List

import altair
import numpy as np
import pandas as pd

import logging
import os
import traceback

log = logging.getLogger("app")
rows_per_page = 10


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
    log.setLevel(os.environ.get("LOG_LEVEL", "INFO").upper())


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
        # log.debug - printed only when LOG_LEVEL is set to DEBUG
        log.info("====== Start serve Function ========")
        q_args_dict = expando_to_dict(q.args)
        log.info(">>>> q.args >>>>")
        for k, v in q_args_dict.items():
            log.info(f"{k}: {v}")
        log.info("<<<< q.args <<<<")
        log.info(f"q.user: {q.user}")
        log.info(f"q.events: {q.events}")

        # First time the app is loaded
        if not q.app.initialized:
            await init_app(q)
            q.app.initialized = True

        # First time a browser(tab) opens the app
        if not q.client.initialized:
            action_taken = True
            await init(q)
            q.client.initialized = True
            await q.page.save()
        else:
            if q.args['#'] and q.args['#'] != q.client.current_tab:
                log.info("========Handle  Tab Change=====")
                log.info(f"Previous tab saved in q.client.current_tab: {q.client.current_tab}")
                # Set new active menu item
                q.page['nav_menu'].value = f'#{q.args["#"]}'
                q.client.current_tab = q.args["#"]

                if q.args['#'] == "details":
                    log.info("========Handle  Tab Change Switch to details=====")
                    # Restore threshold value to the last clicked on
                    log.info(f"previous threshold:{q.client.threshold}")
                    q.page['threshold_card'].items[0].slider.value = q.client.threshold
                    # Display a different tab
                    # q.page["meta"] = q.client.details
                    await render_emp_details(q)

                elif q.args['#'] == "emp_plots":
                    log.info("========Handle  Tab Change Switch to plots=====")
                    # q.page["meta"] = q.client.emp_plots
                    await render_emp_plots(q)

            elif q.args.threshold is not None and q.client.threshold != q.args.threshold:
                log.info("========Handle  Threshold Change=====")
                q.client.threshold = q.args.threshold
                await render_threshold(q)

            elif q.args.render_employee is not None and len(q.args.render_employee) == 1 and \
                    int(q.args.render_employee[0]) != q.client.employee_num:
                q.client.employee_num = int(q.args.render_employee[0])
                await render_emp_shapley(q)

            elif q.events.render_employee and q.events.render_employee.page_change:
                log.info("========Handle  page Change=====")
                q.client.page_offset = q.events.render_employee.page_change.get('offset', 0)
                await render_pagination(q)

            elif q.events.render_employee and q.events.render_employee.reset:
                log.info("========Handle  page Reset=====")
                q.client.page_offset = 0
                await render_pagination(q)

            else:
                # We can get here if user did not change anything.
                # For example, clicked on already selected Employee, or moved threshold slider to the same value
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
    file_path = os.path.abspath(__file__)
    dir_path = os.path.dirname(file_path)
    predictions_file = os.path.join(dir_path, 'static', 'predictions.csv')
    shapley_file = os.path.join(dir_path, 'static', 'shapley_values.csv')
    q.app.predictions = pd.read_csv(predictions_file)
    q.app.predictions = q.app.predictions.rename(columns={'Attrition.Yes': "Prediction"})
    q.app.shapley = pd.read_csv(shapley_file)


async def init(q: Q) -> None:
    log.info("==Start init Function ==")
    q.client.cards = set()
    q.client.dark_mode = False
    q.client.initialized = False
    # Define Layout for Tab Emp Plots
    q.page["meta"] = ui.meta_card(
        box='',
        title='Employee Churn Prediction',
        layouts=[
            ui.layout(
                breakpoint='xs',
                min_height='100vh',
                max_width='1200px',
                zones=[
                    ui.zone(name='header', direction='row', size='120px'),
                    ui.zone(name='body', direction='row', size='1',
                            zones=[ui.zone(name='nav', size='14%'),
                                   ui.zone(name='content',
                                           size='86%',
                                           zones=[ui.zone('horizontal', direction=ui.ZoneDirection.ROW),
                                                  ui.zone('vertical', size='1')])
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
    q.page['nav_menu'] = ui.nav_card(box='nav',
                                     value='#emp_plots',
                                     items=[ui.nav_group('Menu', items=[
                                         ui.nav_item(name='#emp_plots', label='Emp Plots',
                                                     icon='ConnectVirtualMachine'),
                                         ui.nav_item(name='#details', label='Details',
                                                     icon='TestExploreSolid')]),
                                            ui.nav_group('Help', items=[
                                                ui.nav_item(name='#help/contact', label='Contact Us', icon='Help'),
                                            ])])

    # Populate Data for emp_plots Tab
    q.client.churn_pred = altair.Chart(q.app.predictions).mark_bar() \
                                                         .encode(altair.X("Prediction", bin=True), y='count()', ) \
                                                         .properties(width='container', height='container') \
                                                         .interactive() \
                                                         .to_json()

    # Variable importance graph. Get List of columns and importance
    q.client.varimp, q.client.varimp_col = get_varimp(q.app.shapley)

    # Populate Initial Data for details Tab
    # Card with threshold slider description
    q.client.threshold = 0.5
    q.client.churned_employees = q.app.predictions[q.app.predictions['Prediction'] > q.client.threshold]
    q.client.page_offset = 0

    # Set first employee in the table to populate Shapley values for the first time
    q.client.employee_num = q.client.churned_employees['EmployeeNumber'].iloc[0]
    q.client.employee_varimp = get_local_varimp(q.app.shapley[q.app.shapley['EmployeeNumber'] == q.client.employee_num])

    if q.args['#'] == "details":
        await render_emp_details(q)
    else:  # if q.args['#'] is None or q.args['#'] == "emp_plots":
        await render_emp_plots(q)
    log.info("==Complete init Function ==")


async def render_emp_plots(q: Q):
    log.info("==Start render_emp_plots Function ==")
    q.page['nav_menu'].value = '#emp_plots'
    q.client.current_tab = "emp_plots"
    clear_cards(q)  # When routing, drop all the cards except of the main ones (header, sidebar, meta).

    # Add card from already loaded Churn prediction chart
    add_card(q, 'predictions_card', ui.vega_card(box='horizontal', title='Churn Predictions',
                                                 specification=q.client.churn_pred
                                                 ))

    # Add card from already loaded Variable importance graph
    add_card(q, 'varimp_card', ui.plot_card(box='horizontal',
                                            title='Top Factors Affecting Churn',
                                            data=data('feature importance', 5, rows=q.client.varimp),
                                            plot=ui.plot([ui.mark(type='interval', x='=importance', y='=feature',
                                                                  x_min=0, color='#9c3a3a')])
                                            ))
    log.info("==Complete render_emp_plots Function ==")


async def render_emp_details(q: Q):
    """
    Render the details page:
        - Threshold selection card according to last set threshold
        - Employees table
        - Shapley values for the selected (set to first in init function) employee from the Employees table

    :param q:
    :return:
    """
    log.info("==Start render_emp_details Function ==")
    q.page['nav_menu'].value = '#details'
    q.client.current_tab = "details"
    clear_cards(q)  # When routing, drop all the cards except of the main ones (header, sidebar, meta).

    # Card with description for threshold slider card that follows
    add_card(q, 'description_card', ui.form_card(box='vertical', items=[
        ui.text("Use the slider below to change the cutoff for churn prediction and update the statistics.")
    ]
                                                 ))

    add_card(q, 'threshold_card', ui.form_card(box='vertical', items=[ui.slider(name='threshold',
                                                                                label='Prediction Threshold',
                                                                                min=0,
                                                                                max=0.9,
                                                                                step=0.1,
                                                                                value=q.client.threshold,
                                                                                trigger=True,
                                                                                )]))
    # Stats Cards
    add_card(q, 'stats_card', ui.form_card(box='vertical', items=[
        ui.stats([
            ui.stat(label='Number of Employees',
                    value=str(len(q.client.churned_employees)),
                    caption='Predicted Churn Employees'),
            ui.stat(label='% of Employees',
                    value="{0:.0%}".format(len(q.client.churned_employees) / len(q.app.predictions)),
                    caption='Predicted Churn Employees'),
            ui.stat(label='Average Years at the Company', value=str(round(q.client.churned_employees.YearsAtCompany.mean())),
                    caption='Predicted Churn Employees'),
        ], justify='between')]))

    # Churned Employees Table
    cols = ['EmployeeNumber'] + q.client.varimp_col + ["Prediction"]
    add_card(q, 'table_card', ui.form_card(box='vertical', items=[
        ui.table(
            name='render_employee',
            columns=[ui.table_column(name=i, label=i, sortable=True) for i in cols],
            rows=[ui.table_row(name=str(row['EmployeeNumber']),
                               cells=[str(k) for k in row[cols]]) for i, row in
                  q.client.churned_employees[0:rows_per_page].iterrows()],
            pagination=ui.table_pagination(total_rows=len(q.client.churned_employees), rows_per_page=rows_per_page),
            resettable=True,
            events=['page_change', 'reset']
        )]))
    q.client.page_offset = 0

    # Display Shapley values for employee stored in the q.client.employee_num
    add_card(q, 'shap_card',
             ui.plot_card(box='vertical',
                          title='Top Factors Affecting Churn for Employee {}'.format(q.client.employee_num),
                          data=data('feature importance color', 5, rows=q.client.employee_varimp),
                          plot=ui.plot([ui.mark(type='interval', x='=importance', y='=feature', color='=color',
                                                color_domain=['decreases risk', 'increases risk'],
                                                color_range='#28733b #9c3a3a')])
                          ))

    log.info("==Complete render_emp_plots Function ==")


async def render_threshold(q: Q):
    """
    Accept threshold value from slider and Refresh Stats cards and table of employees
    :param q:
    :return:
    """
    log.info("==Start render_threshold Function ==")

    # Get employees for the given threshold
    q.client.churned_employees = q.app.predictions[q.app.predictions['Prediction'] > q.client.threshold]

    # Update Stats cards
    q.page['stats_card'].items[0].stats.items[0].value = str(len(q.client.churned_employees))
    q.page['stats_card'].items[0].stats.items[1].value = "{0:.0%}".format(len(q.client.churned_employees) / len(q.app.predictions))
    q.page['stats_card'].items[0].stats.items[2].value = str(round(q.client.churned_employees.YearsAtCompany.mean()))

    # Update Churned Employees Table
    cols = ['EmployeeNumber'] + q.client.varimp_col + ["Prediction"]
    add_card(q, 'table_card', ui.form_card(box='vertical', items=[
        ui.table(
            name='render_employee',
            columns=[ui.table_column(name=i, label=i, sortable=True) for i in cols],
            rows=[ui.table_row(name=str(row['EmployeeNumber']), cells=[str(k) for k in row[cols]]) for i, row in
                  q.client.churned_employees[0:rows_per_page].iterrows()],
            pagination=ui.table_pagination(total_rows=len(q.client.churned_employees), rows_per_page=rows_per_page),
            resettable=True,
            events=['page_change', 'reset']
        )]))
    q.client.page_offset = 0

    log.info("==Complete render_threshold Function ==")


async def render_pagination(q:Q):
    """
    Handle Page change for table of employees
    :param q:
    :return:
    """
    log.info("==Start render_pagination Function ==")
    cols = ['EmployeeNumber'] + q.client.varimp_col + ["Prediction"]
    # Reset offset to first page
    offset = q.client.page_offset
    q.page['table_card'].items[0].table.rows = [ui.table_row(name=str(row['EmployeeNumber']),
                                                             cells=[str(k) for k in row[cols]]) for i, row in
                                                                               q.client.churned_employees[offset:
                                                                                   (offset + rows_per_page)].iterrows()]
    log.info("==Complete render_pagination Function ==")


async def render_emp_shapley(q: Q):
    """
    Refresh Shapley values for the selected employee.
    :param q:
    :return:
    """
    log.info("==Start render_emp_shapley Function ==")
    q.client.employee_varimp = get_local_varimp(q.app.shapley[q.app.shapley['EmployeeNumber'] == q.client.employee_num])

    # Refresh Shapley Values Plot
    q.page['shap_card'].title = 'Top Factors Affecting Churn for Employee {}'.format(q.client.employee_num)
    q.page['shap_card'].data = q.client.employee_varimp
    log.info("==Complete render_emp_shapley Function ==")


def get_varimp(shapley_vals, top_n=5):
    """
    Get Global variable importance based on Shapley Values
    :param shapley_vals:
    :param top_n:
    :return:
    """
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
    """
    Format Shapley Values for given employee
    :param shapley_vals:
    :param top_n:
    :return:
    """
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


# Use for page cards that should be removed when navigating away.
# For pages that should be always present on screen use q.page[key] = ...
def add_card(q, name, card) -> None:
    log.info("==Start add_card Function for card:" + str(name) + " ==")
    q.client.cards.add(name)
    q.page[name] = card
    log.info("==Complete add_card Function==")


# Remove all the cards related to navigation.
def clear_cards(q, ignore: Optional[List[str]] = []) -> None:
    if not q.client.cards:
        return

    for name in q.client.cards.copy():
        if name not in ignore:
            del q.page[name]
            q.client.cards.remove(name)
