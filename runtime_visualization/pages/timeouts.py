from runtime_visualization.broker import timeout_df

import dash

from dash import html, dcc

import plotly.express as px

id_suffix = "_timeouts"

dash.register_page(__name__, name="Timeouts", order=4)

df = timeout_df

df["Size"] = df["Prozentuale Timeouts"]

# replace size with 5 if size is 0 and set faked_size to True
df["fake_size"] = df["Size"] == 0
df["Size"] = df["Size"].replace(0, 5)

fig = px.scatter_3d(timeout_df, x="number_of_weightclasses", z="number_of_items", y="number_of_knapsacks",
                    color="algorithm", opacity=0.5, size="Size", symbol='fake_size',
                    log_z=True, labels={"number_of_weightclasses": "Anzahl Gewichtsklassen",
                                        "number_of_items": "Anzahl Gegenstände",
                                        "number_of_knapsacks": "Anzahl Rucksäcke",
                                        "algorithm": "Algorithmus",
                                        "fake_size": "keine Timeouts"},
                    symbol_map={True: "diamond", False: "circle-open"},
                    size_max=100)

# the faked sizes should only be shown in the legend by default
fig.for_each_trace(lambda trace: trace.update(visible="legendonly") if "True" in trace.name else None)

layout = html.Div(children=[
    html.H1(children='Timeouts'),
    dcc.Graph(id='timeouts' + id_suffix, mathjax=True, style={'height': '90vh'}, figure=fig)
])
