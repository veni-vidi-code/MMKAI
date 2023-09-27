"""
Diese Datei enthält einige häufiger verwendete Komponenten für die Seite, die in mehreren Dateien verwendet werden.
"""

import dash_bootstrap_components as dbc

from dash import html

_tab_selected_style = {
    'borderTop': '1px solid #d6d6d6',
    'backgroundColor': '#abe2fb',
    "fontWeight": "bold"
}

footer = html.Footer(
    dbc.Container([
        dbc.Row([dbc.Col(
            dbc.Button("Github", color="info", outline=True, href="https://github.com/veni-vidi-code/MMKAI",
                       target="_blank"),
            className="ml-auto pull-left"),
            ],
            className="justify-content-between")],
        fluid=True),
    className="fixed-bottom mb-2")

