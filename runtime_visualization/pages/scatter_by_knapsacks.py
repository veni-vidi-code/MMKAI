from runtime_visualization.broker import data, knapsacks

import dash

from dash import html, dcc, callback, Input, Output

import plotly.express as px

id_suffix = "_by_knapsacks_scatter"

dash.register_page(__name__, name="Laufzeiten nach Rucksäcken", order=2)

layout = html.Div(children=[
    html.H1(children='Laufzeiten nach Rucksäcken'),
    html.Div([
        "Anzahl Rucksäcken:",
        dcc.Slider(0, len(knapsacks) - 1, None, value=0, id="knapsacks" + id_suffix,
                   marks={i: str(j) for i, j in enumerate(knapsacks)}),
    ]),
    html.Br(),
    dcc.Graph(id='runtimes' + id_suffix, mathjax=True, style={'height': '90vh'})
])


@callback(Output('runtimes' + id_suffix, 'figure'), Input('knapsacks' + id_suffix, 'value'))
def update_runtimes_2(number_of_knapsacks):
    df = data[data["number_of_knapsacks"] == knapsacks[number_of_knapsacks]]

    fig = px.scatter_3d(df, x="number_of_weightclasses", y="number_of_items", z="required_time",
                        color="algorithm", opacity=0.5, symbol='Timeout',
                        log_y=True, labels={"number_of_weightclasses": "Anzahl Gewichtsklassen",
                                            "number_of_items": "Anzahl Gegenstände",
                                            "required_time": "Laufzeit (s)",
                                            "algorithm": "Algorithmus"})

    return fig
