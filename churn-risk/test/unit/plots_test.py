import pytest
import src.plots as plots
from plotly import graph_objects as go


def test_pie_chart_figure_generation():
    labels = ['Day Charges', 'Evening Charges', 'Night Charges', 'Intl Charges']
    values = [10, 15, 5, 10]
    layout = go.Layout(margin=go.layout.Margin(l=0, r=0, b=0, t=0, pad=0, autoexpand=True))
    title = 'Test_Chart'
    expected_type = 'pie'

    pie_chart = plots.generate_figure_pie_of_target_percent(title, labels, values, layout)
    plot_data = pie_chart.to_dict()['data'][0]

    assert title == plot_data['title']['text']
    assert labels == plot_data['labels']
    assert values == plot_data['values']
    assert expected_type == plot_data['type']


def test_pie_chart_generation_missing_params():
    with pytest.raises(TypeError, match=r".* missing 1 required positional argument: .*"):
        labels = ["Day Charges", "Evening Charges", "Night Charges", "Intl Charges"]
        values = [10, 15, 5, 10]
        layout = go.Layout(margin=go.layout.Margin(l=0, r=0, b=0, t=0, pad=0, autoexpand=True))
        plots.generate_figure_pie_of_target_percent(labels, values, layout)


def test_html_pie_chart_conversion():
    layout = go.Layout(margin=go.layout.Margin(l=0, r=0, b=0, t=0, pad=0, autoexpand=True))
    title = 'Test_Chart'
    labels = ["Day Charges", "Evening Charges", "Night Charges", "Intl Charges"]
    values = [10, 15, 5, 10]
    expected_layout = '{"margin": {"autoexpand": true, "b": 0, "l": 0, "pad": 0, "r": 0, "t": 0}'
    expected_title = '"title": {"text": "Test_Chart"}'
    expected_labels = '"labels": ["Day Charges", "Evening Charges", "Night Charges", "Intl Charges"]'
    expected_values = '"values": [10, 15, 5, 10]'
    expected_type = '"type": "pie"'
    pie_chart = plots.generate_figure_pie_of_target_percent(title, labels, values, layout)
    html_plot = plots.convert_plot_to_html(None, pie_chart, 'cdn', False)

    assert expected_title in html_plot
    assert expected_labels in html_plot
    assert expected_values in html_plot
    assert expected_type in html_plot
    assert expected_layout in html_plot


def test_html_pie_chart_conversion_missing_param():
    with pytest.raises(TypeError, match=r".* missing 1 required positional argument: .*"):
        title = 'Test_Chart'
        labels = ["Day Charges", "Evening Charges", "Night Charges", "Intl Charges"]
        values = [10, 15, 5, 10]
        layout = go.Layout(margin=go.layout.Margin(l=0, r=0, b=0, t=0, pad=0, autoexpand=True))
        pie_chart = plots.generate_figure_pie_of_target_percent(title, labels, values, layout)
        plots.convert_plot_to_html(None, pie_chart, 'cdn')
