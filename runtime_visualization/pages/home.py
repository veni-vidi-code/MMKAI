import dash
import dash_bootstrap_components as dbc
from dash import html


dash.register_page(__name__, path='/', order=0, name='Home')
"""
Übersichtsseite
"""


def layout():  # A function is necessary bacause page registry is not complete at import time
    return html.Div([html.Br(),
                     html.Div([dbc.Button(page["name"], color="info", href=page["path"])
                               for page in dash.page_registry.values()
                               if page["module"] != "pages.not_found_404" and page["path"] != "/"],
                              className="d-grid gap-2 col-6 mx-auto align-items-center", id="home-button-container")])
