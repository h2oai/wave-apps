from plotly import graph_objects as go
from plotly import io as pio

from h2o_wave import ui

import io
import base64


def html_pie_of_target_percent(title, labels, values):

    config = {
        'scrollZoom': False,
        'displayModeBar': None
    }

    layout = go.Layout(
        margin=go.layout.Margin(
            l=0,
            r=0,
            b=0,
            t=0,
            pad=0,
            autoexpand=True
        )
    )

    fig = go.Figure(data=[go.Pie(title=title, labels=labels, values=values)], layout=layout)
    fig.update_traces(hoverinfo='label+percent', textinfo='value', textfont_size=14)
    return pio.to_html(fig, validate=False, include_plotlyjs='cdn', config=config)


def tall_stat_card_dollars(df, cust_id, x_variable, box, company_color):

    df['rank'] = df[x_variable].rank(pct=True)
    cust = df[df["Phone_No"] == cust_id]

    card = ui.tall_gauge_stat_card(
        box=box,
        title=x_variable,
        value='=${{intl foo minimum_fraction_digits=2 maximum_fraction_digits=2}}',
        aux_value='={{intl bar style="percent" minimum_fraction_digits=0 maximum_fraction_digits=0}}',
        plot_color=company_color,
        progress=df['rank'].values[0],
        data=dict(foo=cust[x_variable].values[0], bar=df['rank'].values[0]),
    )
    return card


def wide_stat_card_dollars(df, cust_id, x_variable, box, company_color):

    df['rank'] = df[x_variable].rank(pct=True)
    cust = df[df["Phone_No"] == cust_id]

    card = ui.wide_gauge_stat_card(
        box=box,
        title=x_variable,
        value='=${{intl foo minimum_fraction_digits=2 maximum_fraction_digits=2}}',
        aux_value='={{intl bar style="percent" minimum_fraction_digits=0 maximum_fraction_digits=0}}',
        plot_color=company_color,
        progress=df['rank'].values[0],
        data=dict(foo=cust[x_variable].values[0], bar=df['rank'].values[0]),
    )
    return card


def get_image_from_matplotlib(matplotlib_obj):
    buffer = io.BytesIO()
    matplotlib_obj.savefig(buffer, format='png')
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode('utf-8')
