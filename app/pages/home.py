from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc

# Reusable UI components
from components.buttons import (
    data_version_toggle,
    pollutant_type_dropdown,
    metric_dropdown,
    primary_button,
    secondary_button,
    success_button,
    danger_button,
)

# -------- Section UIs --------
def map_section():
    return html.Div([
        html.H3("Global Pollution Map", className="mb-3"),

        # Common Filters (only for Map)
        dbc.Card([
            dbc.CardHeader("Common Filters", className="fw-semibold"),
            dbc.CardBody([
                dbc.Row([
    dbc.Col(
        html.Div([
            html.Label("Data Version", className="form-label fw-semibold mb-1"),
            data_version_toggle(id="data-version", value="v1")
        ]),
        md=4
    ),
    dbc.Col(
        html.Div([
            html.Label("Pollutant Type", className="form-label fw-semibold mb-1"),
            pollutant_type_dropdown(id="pollutant-type")
        ]),
        md=4
    ),
    dbc.Col(
        html.Div([
            html.Label("Metric", className="form-label fw-semibold mb-1"),
            metric_dropdown(id="metric")
        ]),
        md=4
    ),
], className="g-2"),

                # dbc.Row([
                #     dbc.Col(
                #         dbc.ButtonGroup([
                #             primary_button(id="apply-filters-btn", label="Apply"),
                #             danger_button(id="reset-filters-btn", label="Reset"),
                #             secondary_button(id="back-btn", label="Back", href="/overview"),
                #         ]),
                #         md=12, className="mt-2"
                #     )
                # ])
            ]),
        ], className="mb-3"),

        # Map canvas
        dbc.Card([
            dbc.CardBody(
                html.Div(
                    "Map will go here...",
                    className="text-muted",
                    style={
                        "height": "420px",
                        "display": "flex",
                        "alignItems": "center",
                        "justifyContent": "center",
                        "border": "1px dashed #ced4da",
                        "borderRadius": "6px",
                    },
                )
            )
        ]),
    ])


def blank_placeholder(text):
    return dbc.Alert(text, color="secondary", className="mb-0")


# -------- Page Layout --------
layout = html.Div([html.Div(id="home-content")], className="p-0")


# -------- Router for Home subsections --------
@callback(Output("home-content", "children"),
          Input("url", "pathname"))
def render_home_section(pathname: str):
    if pathname in ("/home", "/home/map"):
        return map_section()
    elif pathname == "/home/change":
        return blank_placeholder("Percent Change — coming soon.")
    elif pathname == "/home/data":
        return blank_placeholder("Data & Download — coming soon.")
    elif pathname == "/home/about":
        return blank_placeholder("About — coming soon.")
    return blank_placeholder("Unknown Home section.")
