from dash import html
import dash_bootstrap_components as dbc

layout = dbc.Card(
    dbc.CardBody([
        html.H2("States", className="mb-3"),
        html.P("States page — placeholder.", className="text-muted")
    ]),
    className="shadow-sm"
)