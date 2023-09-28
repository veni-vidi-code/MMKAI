"""
Diese Datei enthält einige häufiger verwendete Komponenten für die Seite, die in mehreren Dateien verwendet werden.
"""
import os
from os.path import exists

import dash_bootstrap_components as dbc

from dash import dcc, html, Output, Input, State

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
            dbc.Col(dbc.Button("Info", n_clicks=0, color="info", id="btn-info", outline=True),
                    className="pull-right d-grid gap-2 col-6 mx-aut")],
            className="justify-content-between")],
        fluid=True),
    className="fixed-bottom mb-2")

canvas = dbc.Offcanvas("", id="offcanvas", is_open=False, title="")


def add_callbacks(app):
    app.clientside_callback("function(n, is_open) {return !is_open;}",
                            Output('offcanvas', 'is_open'),
                            Input('btn-info', 'n_clicks'),
                            State('offcanvas', 'is_open'), prevent_initial_call=True)

    @app.callback(Output('offcanvas', 'title'),
                  Output('offcanvas', 'children'),
                  Input('url', 'pathname'))
    def update_offcanvas(pathname):
        # read markdown file from assets/mardownpagesexplanaition
        # ensures no relative paths are used
        pathname = pathname.replace(".", "")
        pathname = pathname.replace("~", "")

        # replaces - with _ to get the correct filename
        filename = pathname.replace("-", "_")[1:] + ".md"

        if filename == ".md":
            filename = "index.md"
        path = os.path.join(os.path.dirname(__file__), "assets/markdownpagesexplanation/" + filename)
        if exists(path):
            with open(path, "r", encoding="utf-8") as f:
                title = f.readline().strip("#").strip()
                markdown = f.read()

            if title == "":
                title = "Info"
                for page in app.page_registry.values():
                    if page["path"] == pathname:
                        title = page["name"]
                        break

            return title, dcc.Markdown(markdown, mathjax=True)
        else:
            return "Info", dcc.Markdown("Zu dieser Seite gibt es keine Info")
