import base64
import io

from h2o_wave import ui
from plotly import graph_objects as go
from plotly import io as pio


def generate_figure_pie_of_target_percent(title, labels, values, layout):
    fig = go.Figure(
        data=[go.Pie(title=title, labels=labels, values=values)], layout=layout
    )
    return fig.update_traces(
        hoverinfo="label+percent", textinfo="value", textfont_size=14
    )


def convert_plot_to_html(config, fig, include_plotlyjs, validate):
    return pio.to_html(
        fig, validate=validate, include_plotlyjs=include_plotlyjs, config=config
    )


def tall_stat_card_dollars(df, cust_id, x_variable, box, company_color):

    df["rank"] = df[x_variable].rank(pct=True)
    cust = df[df["Phone_No"] == cust_id]

    card = ui.tall_gauge_stat_card(
        box=box,
        title=x_variable,
        value="=${{intl charge minimum_fraction_digits=2 maximum_fraction_digits=2}}",
        aux_value='={{intl rank style="percent" minimum_fraction_digits=0 maximum_fraction_digits=0}}',
        plot_color=company_color,
        progress=df["rank"].values[0],
        data=dict(charge=cust[x_variable].values[0], rank=df["rank"].values[0]),
    )
    return card


def wide_stat_card_dollars(df, cust_id, x_variable, box, company_color):

    df["rank"] = df[x_variable].rank(pct=True)
    cust = df[df["Phone_No"] == cust_id]

    card = ui.wide_gauge_stat_card(
        box=box,
        title=x_variable,
        value="=${{intl charge minimum_fraction_digits=2 maximum_fraction_digits=2}}",
        aux_value='={{intl rank style="percent" minimum_fraction_digits=0 maximum_fraction_digits=0}}',
        plot_color=company_color,
        progress=df["rank"].values[0],
        data=dict(charge=cust[x_variable].values[0], rank=df["rank"].values[0]),
    )
    return card


def get_image_from_matplotlib(matplotlib_obj):
    buffer = io.BytesIO()
    matplotlib_obj.savefig(buffer, format="png")
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode("utf-8")
