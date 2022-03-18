import pandas as pd
import toml
from h2o_wave import Q, app, data, main, ui
from loguru import logger
from matplotlib import pyplot


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

    elif q.args.column_selector is not None:
        # The user wants to view another column
        q.client.selected_column = q.args.column_selector
        q.page["header"].items[0].dropdown.value = q.args.column_selector
        create_app_ui(q)

    await q.page.save()


async def initialize_client(q: Q) -> None:
    """
    Information which may be unique for each browser tab that is running this app - setup the initial state
    for the app to work for this new tab
    """

    if q.client.toml is None:
        logger.info("initializing the app for a new client")
        q.client.toml = toml.load("app.toml")

    q.client.df = pd.read_csv(q.client.toml["Data"]["FileLocation"])
    q.client.target_column = q.client.toml["Data"]["TargetColumn"]
    q.client.selected_column = q.client.df.columns.tolist()[0]

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
                height="100vh",
                zones=[
                    ui.zone(
                        "main",
                        size="1",
                        zones=[
                            ui.zone("header"),
                            ui.zone("body", size="1"),
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
        items=[
            ui.dropdown(
                name="column_selector",
                label="Choose a Column",
                choices=[ui.choice(name=col, label=col) for col in q.client.df.columns],
                value=q.client.selected_column,
                width="300px",
                trigger=True,
            ),
        ],
    )
    q.page["footer"] = ui.footer_card(
        box="footer", caption="Made with 💛 using H2O Wave."
    )


def create_app_ui(q: Q):
    """
    Creating distribution plots for each target, this is a groupby for objects or a histogram for numbers
    """
    logger.info("aggregating and plotting the data")

    if (q.client.df[q.client.selected_column].dtypes == "object") or (
        len(q.client.df[q.client.selected_column].unique()) < 10
    ):
        # We use pandas group by for categorical columns
        for v in q.client.df[q.client.target_column].unique():
            df = q.client.df[q.client.df[q.client.target_column] == v]

            agg = (
                df.groupby([q.client.selected_column]).size().reset_index(name="count")
            )
            agg["value"] = agg[q.client.selected_column]

            q.page[f"plot_{v}"] = ui.plot_card(
                box="body",
                title=f"{q.client.target_column}: {v}",
                data=data(
                    fields=agg.columns.tolist(),
                    rows=agg.values.tolist(),
                ),
                plot=ui.plot(
                    marks=[
                        ui.mark(
                            type="interval",
                            x=f"=value",
                            x_title=q.client.selected_column,
                            x_scale="category",
                            y="=count",
                            y_title="Count",
                        )
                    ]
                ),
            )
    else:
        # We use the matplot lib histogram function for numeric values
        for v in q.client.df[q.client.target_column].unique():
            hist = pyplot.hist(
                q.client.df[q.client.df[q.client.target_column] == v][
                    q.client.selected_column
                ],
                range=(
                    q.client.df[q.client.selected_column].min(),
                    q.client.df[q.client.selected_column].max(),
                ),
            )
            hist_df = pd.DataFrame(list(zip(hist[0], hist[1])), columns=["Y", "X"])

            q.page[f"plot_{v}"] = ui.plot_card(
                box="body",
                title=f"{q.client.target_column}: {v}",
                data=data(
                    fields=hist_df.columns.tolist(),
                    rows=hist_df.values.tolist(),
                ),
                plot=ui.plot(
                    marks=[
                        ui.mark(
                            type="interval",
                            x="=X",
                            x_title=q.client.selected_column,
                            y="=Y",
                            y_title="Count",
                        )
                    ]
                ),
            )
