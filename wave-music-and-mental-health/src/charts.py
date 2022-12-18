from h2o_wave import Q, ui
from siuba import *
from siuba.siu import call
import plotly.express as px
import plotly.io as pio
from plotly import graph_objects as go

pio.templates.default = "plotly_dark"


def update_chart(fig):

    return fig.update(
        layout=go.Layout(margin=dict(t=40, r=0, b=40, l=0), legend=dict(yanchor="top", y=0.95, xanchor="left", x=0.01))
    )


# show table of data
async def show_table(df):
    return ui.table(
        name="table",
        height="410px",
        # Add pagination attribute to make your table paginated.
        pagination=ui.table_pagination(total_rows=100, rows_per_page=5),
        events=["page_change"],
        columns=[ui.table_column(name=x, label=x) for x in df.columns.tolist()],
        rows=[ui.table_row(name=str(i), cells=list(map(str, df.values.tolist()[i]))) for i in df.index[0:100]],
    )


async def age_hist(df):
    fig = df >> call(px.histogram, x="age", data_frame=_, labels={"age": "Age"})
    update_chart(fig)
    html = pio.to_html(fig, config=None, auto_play=True, include_plotlyjs="cdn")
    return html


async def streaming_service(df):
    fig = df >> call(
        px.histogram,
        x="primary_streaming_service",
        data_frame=_,
        labels={"primary_streaming_service": "Primary Streaming Service"},
    )
    fig.update_xaxes(categoryorder="total descending")
    update_chart(fig)
    html = pio.to_html(fig, config=None, auto_play=True, include_plotlyjs="cdn")
    return html


async def fav_age_effect(df):
    fig = df >> call(
        px.histogram,
        x="fav_genre",
        y="age",
        color="music_effects",
        data_frame=_,
        text_auto=True,
        histfunc="avg",
        barmode="group",
        title="Music Effect on Listeners - Age",
        labels={"fav_genre": "Fav Genre", "age": "Age"},
    )

    update_chart(fig)
    html = pio.to_html(fig, config=None, auto_play=True, include_plotlyjs="cdn")
    return html


async def fav_depression(df):
    fig = df >> call(
        px.histogram,
        x="fav_genre",
        y="depression",
        color="music_effects",
        data_frame=_,
        text_auto=True,
        histfunc="avg",
        barmode="group",
        title="Music Effect on Listeners - Depression",
        labels={"fav_genre": "Fav Genre", "depression": "Depression"},
    )

    fig.update_yaxes(title="Depression", range=[0, 10])
    update_chart(fig)
    html = pio.to_html(fig, config=None, auto_play=True, include_plotlyjs="cdn")
    return html


async def fav_insomnia(df):
    fig = df >> call(
        px.histogram,
        y="insomnia",
        x="fav_genre",
        color="music_effects",
        data_frame=_,
        text_auto=True,
        histfunc="avg",
        barmode="group",
        title="Music Effect on Listeners - Insomnia",
        labels={"fav_genre": "Fav Genre", "insomnia": "Insomnia"},
    )

    fig.update_yaxes(title="Insomnia", range=[0, 10])
    update_chart(fig)
    html = pio.to_html(fig, config=None, auto_play=True, include_plotlyjs="cdn")
    return html
