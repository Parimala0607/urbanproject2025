from dash import html
import dash_bootstrap_components as dbc

layout = dbc.Card(
    dbc.CardBody([
        html.H2("Help & Guide", className="mb-3"),
        html.P("Docs and guidance will appear here.", className="text-muted")
    ]),
    className="shadow-sm"
)