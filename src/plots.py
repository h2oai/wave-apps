import pandas as pd

from plotly import graph_objects as go
from plotly import io as pio

from h2o_wave import ui

import io
import base64

def html_map_of_target_percent(data_location, target_variable, state_variable, company_color):
    df = pd.read_csv(data_location)
    grp = df.groupby([state_variable, target_variable]).size()

    state_pcts = grp.groupby(level=0).apply(lambda x: 100 * x / float(x.sum())).reset_index(name="Percent")
    state_pcts = state_pcts[state_pcts[target_variable]]

    fig = go.Figure(data=go.Choropleth(
        locations=state_pcts[state_variable],  # Spatial coordinates
        z=round(state_pcts['Percent'], 2).astype(float),  # Data to be color-coded
        locationmode='USA-states',  # set of locations match entries in `locations`
        colorscale=["white", company_color, "black"],  # go from white to black with color being company we demo to
        colorbar_title=f"{target_variable} Percent",
    ))

    fig.update_layout(
        title_text=f'Percent of {target_variable} by {state_variable}',
        geo_scope='usa',  # limit map scope to USA
    )

    config = {
        'scrollZoom': False,
        'displayModeBar': None
    }

    return pio.to_html(fig, validate=False, include_plotlyjs='cdn', config=config)


def html_pie_of_target_percent(title, labels, values):

    config = {
        'scrollZoom': False,
        'displayModeBar': None
    }

    fig = go.Figure(data=[go.Pie(title=title, labels=labels, values=values)])

    fig.update_traces(hoverinfo='label+percent', textinfo='value', textfont_size=20)

    return pio.to_html(fig, validate=False, include_plotlyjs='cdn', config=config)


def html_hist_of_target_percent(data_location, target_varible, x_variable, company_color):
    df = pd.read_csv(data_location)

    event = df[df[target_varible]][x_variable]
    nonevent = df[~df[target_varible]][x_variable]

    fig = go.Figure()
    fig.add_trace(go.Histogram(x=event, name=target_varible, opacity=0.75, histnorm="probability", bingroup=1,
                               marker=dict(color='black')))
    fig.add_trace(go.Histogram(x=nonevent, name=f"Non-{target_varible}", opacity=0.75, histnorm="probability",
                               bingroup=1, marker=dict(color=company_color)))

    fig.update_layout(
        title_text=f'Percent of {x_variable} by {target_varible}',
        barmode='overlay',
        plot_bgcolor="#FFF",
        xaxis=dict(
            title=x_variable,
            showgrid=False  # Removes X-axis grid lines
        ),
        yaxis=dict(
            title="Percent of Population",
            showgrid=False,  # Removes Y-axis grid lines
        )
    )

    config = {
        'scrollZoom': False,
        'displayModeBar': None
    }

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
