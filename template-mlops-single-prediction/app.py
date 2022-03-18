import json

import httpx
import toml
from h2o_wave import Q, app, expando_to_dict, main, ui, data
from loguru import logger


@app("/")
async def serve(q: Q) -> None:
    """
    Handle client interactions with the application
    """
    logger.info("handling a client request")

    if not q.client.initialized:
        # The browser tab has not been to this app instance before
        await initialize_client(q)
        create_base_ui(q)
        create_app_ui(q)

    elif q.args.make_prediction_button:
        #  The user wants to make a prediction
        await update_app_ui(q)

    if q.client.show_error_dialog:
        # The user wants to use a model deployment that we cannot successfully connect to
        show_error_dialog(q)
        q.client.show_error_dialog = False

    await q.page.save()


async def initialize_client(q: Q) -> None:
    """
    Information which may be unique for each browser tab that is running this app - setup the initial state
    for the app to work for this new tab
    """

    if q.client.toml is None:
        logger.info("initializing the app for a new client")
        q.client.toml = toml.load("app.toml")

    # From MLOps, get the expected fields for the deployment and an example row
    await mlops_get_sample_request(q)

    if q.client.show_error_dialog:
        return

    # From MLOps, get a prediction for the example row
    await mlops_get_single_prediction(q)

    if q.client.show_error_dialog:
        return

    # Tracking whether this specific browser tab has been setup or not
    q.client.initialized = True


def create_base_ui(q: Q) -> None:
    """
    Handling the basic frontend for our application: meta information about the app, a header, body, and footer
    """
    logger.info("creating the base ui")

    q.page["meta"] = ui.meta_card(
        box="",
        title=q.client.toml["Brand"]["Title"],
        theme=q.client.toml["Brand"]["Theme"],
        icon=q.client.toml["Brand"]["Image"],
        layouts=[
            ui.layout(
                breakpoint="xs",  # Will work for mobile and desktop - ensure we make content that works
                width="1200px",
                zones=[
                    ui.zone(
                        "main",
                        zones=[
                            ui.zone("header"),
                            ui.zone("body"),
                            ui.zone("footer"),
                        ],
                    )
                ],
            )
        ],
    )
    q.page["header"] = ui.header_card(
        box="header",
        title=q.client.toml["Brand"]["Title"],
        subtitle=q.client.toml["Brand"]["Subtitle"],
        image=q.client.toml["Brand"]["Image"],
    )
    q.page["footer"] = ui.footer_card(
        box="footer", caption="Made with 💛 using H2O Wave."
    )


def create_app_ui(q: Q):
    """
    Create a list of UI elements to show to the end user based on the deployment in MLOps
    """
    logger.info("dynamically creating a form with inputs for this deployment")

    q.page["predictions"] = ui.plot_card(
        box=ui.box("body", height="10%"),
        title="",
        data=data(
            fields=["field", "prediction", "group"],
            rows=[[q.client.prediction_fields[i], float(q.client.single_prediction_value[i]), ""] for i in range(len(q.client.prediction_fields))]
        ),
        plot=ui.plot(marks=[ui.mark(
            type="interval",
            x="=prediction", y="=group", color="field", stack="auto", y_min=0,
        )])
    )

    # Create a list of all ui objects that we want to show in our Single Prediction form card
    form_items = [
        ui.inline(
            items=[
                ui.text_xl("Input your features"),
                ui.button(
                    name="make_prediction_button", label="Make Prediction", primary=True
                ),
            ],
            justify="between",
        ),
    ]

    # Add a textbox for each data-field for our deployment
    for i in range(len(q.client.model_fields)):
        form_items.append(
            ui.textbox(
                # TODO: Column names can be weird - test what happens for edge cases - "My Column with Spaces!"
                name=f"col_{q.client.model_fields[i]}",  # This name will be used to get the values in the textbox
                label=q.client.model_fields[i],
                value=q.client.single_row[i],
            )
        )

    q.page["input_form"] = ui.form_card(box=ui.box("body"), items=form_items)


async def update_app_ui(q: Q) -> None:
    """
    Update the form card with predictions based on the user's feature inputs
    """
    logger.info("dynamically recreating a form for the user's app details")

    # Save the feature-input values for our end user
    user_input_dictionary = expando_to_dict(q.args)
    for key in user_input_dictionary:
        if key.startswith("col_"):
            col_name = key.lstrip("col_")
            col_index = q.client.model_fields.index(col_name)
            q.client.single_row[col_index] = user_input_dictionary[key]

    # Send the data to MLOps and save the prediction
    await mlops_get_single_prediction(q)

    if q.client.show_error_dialog:
        return

    # Update the page with the new prediction values
    q.page["predictions"].data = [[
        q.client.prediction_fields[i],
        float(q.client.single_prediction_value[i]),
        ""
    ] for i in range(len(q.client.prediction_fields))]


def show_error_dialog(q: Q) -> None:
    """
    This app primarily connects to deployments which are not always going to be healthy
    this ui dialog informs our users that something went wrong
    """
    logger.info(
        "informing the user that something when wrong when talking to their deployment"
    )

    q.page["meta"].side_panel = None

    q.page["meta"].dialog = ui.dialog(
        title="Something went wrong!",
        items=[
            ui.text(str(q.client.status_code)),
            ui.text("Please check the health of your deployment in MLOps."),
        ],
        closable=True,
    )


async def mlops_get_sample_request(q: Q) -> None:
    """
    Get the schema and example row from MLOps for a specific deployment, save the details at the client level
    """

    url = q.client.toml["Model"]["Endpoint"] + "/sample_request"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
    except Exception as ex:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)

        q.client.show_error_dialog = True
        q.client.status_code = message
        return

    if response.status_code == 200:
        logger.info("successfully getting sample request for deployment")

        r = json.loads(response.text)

        q.client.show_error_dialog = False
        q.client.model_fields = r["fields"]
        q.client.single_row = r["rows"][0]

    else:
        logger.info("encountering issues getting sample request for deployment")

        q.client.show_error_dialog = True
        q.client.status_code = response.status_code


async def mlops_get_single_prediction(q: Q) -> None:
    """
    Get the schema and example row from MLOps for a specific deployment, save the details at the client level
    """
    url = q.client.toml["Model"]["Endpoint"] + "/score"

    dictionary = {"fields": q.client.model_fields, "rows": [q.client.single_row]}
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=dictionary)

    if response.status_code == 200:
        logger.info("successfully getting prediction for deployment")

        r = json.loads(response.text)

        q.client.show_error_dialog = False
        q.client.prediction_fields = r["fields"]
        q.client.single_prediction_value = r["score"][0]

    else:
        logger.info("encountering errors getting sample request for deployment")

        q.client.show_error_dialog = False
        q.client.status_code = response.status_code
