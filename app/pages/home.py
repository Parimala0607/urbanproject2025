from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc

# -------- Section UIs --------
def map_section():
    return html.Div([
        html.H3("Global Pollution Map", className="mb-3"),

        # Common Filters (only for Map)
        dbc.Card([
            dbc.CardHeader("Common Filters", className="fw-semibold"),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col(dbc.ButtonGroup([
                        dbc.Button("Version 1", id="btn-v1", color="primary", outline=False, n_clicks=0),
                        dbc.Button("Version 2", id="btn-v2", color="secondary", outline=True, n_clicks=0),
                    ]), md=4),

                    dbc.Col(dbc.Select(
                        id="sel-pollutant",
                        options=[{"label": "PM₂.₅", "value": "pm25"},
                                 {"label": "NO₂", "value": "no2"}],
                        value="pm25"
                    ), md=4),

                    dbc.Col(dbc.Select(
                        id="sel-metric",
                        options=[{"label": "Concentration", "value": "conc"},
                                 {"label": "Percentile (p95)", "value": "p95"}],
                        value="conc"
                    ), md=4),
                ], className="g-2"),
            ]),
        ], className="mb-3"),

        # Map canvas
        dbc.Card([
            dbc.CardBody(
                html.Div("Map will go here...",
                         className="text-muted",
                         style={"height": "420px",
                                "display": "flex",
                                "alignItems": "center",
                                "justifyContent": "center",
                                "border": "1px dashed #ced4da",
                                "borderRadius": "6px"})
            )
        ])
    ])

def blank_placeholder(text):
    return dbc.Alert(text, color="secondary", className="mb-0")

# -------- Page Layout --------
layout = html.Div(
    [
        
        html.Div(id="home-content")
    ],
    className="p-0"
)

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
