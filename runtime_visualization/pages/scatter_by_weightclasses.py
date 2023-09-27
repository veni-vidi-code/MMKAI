from runtime_visualization.broker import data, weightclasses

import dash

from dash import html, dcc, callback, Input, Output

import plotly.express as px

id_suffix = "_by_weightclass_scatter"

dash.register_page(__name__, name="Laufzeiten nach Gewichtsklassen", order=1)

layout = html.Div(children=[
    html.H1(children='Laufzeiten nach Gewichtsklassen'),
    html.Div([
        "Anzahl Gewichtsklassen:",
        dcc.Slider(0, len(weightclasses) - 1, None, value=0, id="weightclasses" + id_suffix,
                   marks={i: str(j) for i, j in enumerate(weightclasses)}),
    ]),
    html.Br(),
    dcc.Graph(id='runtimes' + id_suffix, mathjax=True, style={'height': '90vh'})
])


@callback(Output('runtimes' + id_suffix, 'figure'), Input('weightclasses' + id_suffix, 'value'))
def update_runtimes_1(number_of_weightclasses):
    df = data[data["number_of_weightclasses"] == weightclasses[number_of_weightclasses]]

    fig = px.scatter_3d(df, x="number_of_knapsacks", y="number_of_items", z="required_time",
                        color="algorithm", opacity=0.5, symbol='Timeout',
                        log_y=True, labels={"number_of_knapsacks": "Anzahl Rucksäcke",
                                            "number_of_items": "Anzahl Gegenstände",
                                            "required_time": "Laufzeit (s)",
                                            "algorithm": "Algorithmus"})

    return fig
