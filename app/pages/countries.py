from dash import html
import dash_bootstrap_components as dbc

layout = dbc.Card(
    dbc.CardBody([
        html.H2("Countries", className="mb-3"),
        html.P("Countries page — placeholder.", className="text-muted")
    ]),
    className="shadow-sm"
)