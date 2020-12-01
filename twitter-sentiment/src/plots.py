from plotly import graph_objects as go
from plotly.io import to_html


def generate_figure_pie_of_target_percent(scores):
    """
    Generates a pie chart from the given information

    :param scores: Popularity score of the tweets

    :return: plotly figure object
    """
    colors = ['#37536D', ] * 4
    traces = [go.Pie(title="", labels=list(scores.keys()), values=list(scores.values()), hole=0.8),
              go.Bar(name="score", marker_color=colors, x=list(scores.keys()), y=list(scores.values()))]

    fig = go.Figure(data=traces, layout=go.Layout(
        margin=go.layout.Margin(l=0, r=0, b=0, t=0, pad=0, autoexpand=True),
        xaxis=go.layout.XAxis(domain=[0.33, 0.67]),
        yaxis=go.layout.YAxis(domain=[0.33, 0.67])

    ))
    return fig


def convert_plot_to_html(fig, include_plotlyjs, validate):
    """
        Converts given plotly figure object to an HTML string representation

        :param fig: Figure object or dict representing a figure
        :param include_plotlyjs: bool or string (default True)
                                Specifies how the plotly.js library is included/loaded in the output div string.
        :param validate: True if the figure should be validated before being converted to JSON, False otherwise.

        :return: Representation of figure as an HTML div string
        """
    return to_html(
        fig, validate=validate, include_plotlyjs=include_plotlyjs
    )
