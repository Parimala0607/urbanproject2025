from dash import html
import dash_bootstrap_components as dbc

layout = dbc.Card(
    dbc.CardBody([
        html.H2("Overview", className="mb-3"),
        html.P("Overview content coming soon.", className="text-muted")
    ]),
    className="shadow-sm"
)