import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc

# Components
from components.sidebar import sidebar
from components.navbar import navbar
from components.footer import footer

# Pages
from pages import (
    overview,
    home,
    networks,
    countries,
    states,
    help_guide,
)

external_stylesheets = [
    dbc.themes.FLATLY,
    "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.css",
]

app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=external_stylesheets,
    assets_folder="assets",
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
server = app.server

app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    navbar,

    # Content stripe (fills viewport height via CSS)
    html.Div(
        dbc.Container(
            # We'll swap this grid depending on the pathname
            html.Div(id="main-grid"),
            fluid=True,
            className="content-container",
        ),
        className="content-stripe",
    ),

    html.Footer(footer, className="site-footer"),
])

# ---- Build grid with/without sidebar depending on the route ----
@app.callback(Output("main-grid", "children"), Input("url", "pathname"))
def render_main_grid(pathname):
    if pathname and pathname.startswith("/home"):
        # Two-column layout with sidebar on Home pages
        return dbc.Row([
            dbc.Col(
                dbc.Card(sidebar, className="sidebar-card shadow-sm"),
                xs=12, md=3, lg=3,
                className="stretch-col",
            ),
            dbc.Col(
                dbc.Card(html.Div(id="page-content"), className="content-card shadow-sm p-4"),
                xs=12, md=9, lg=9,
                className="stretch-col",
            ),
        ], className="gx-4")
    else:
        # Single-column full-width layout (no sidebar) on non-Home pages
        return dbc.Row([
            dbc.Col(
                dbc.Card(html.Div(id="page-content"), className="content-card shadow-sm p-4"),
                xs=12, md=12, lg=12,
                className="stretch-col",
            ),
        ], className="gx-4")

# ---- Routing ----
@app.callback(Output("page-content", "children"), Input("url", "pathname"))
def display_page(pathname):
    # Overview is landing (also handle "/")
    if pathname in ("/", "/overview"):
        return overview.layout
    elif pathname and pathname.startswith("/home"):
        return home.layout
    elif pathname == "/networks":
        return networks.layout
    elif pathname == "/countries":
        return countries.layout
    elif pathname == "/states":
        return states.layout
    elif pathname == "/help_guide":
        return help_guide.layout
    else:
        return html.Div([
            html.H2("404 — Page not found", className="text-danger"),
            html.P(f"No page registered for: {pathname}")
        ], className="p-4")

# ---- Dynamic active highlighting (blue pill on the current page) ----
@app.callback(
    [
        Output("link-overview",  "active"),
        Output("link-home",      "active"),
        Output("link-networks",  "active"),
        Output("link-countries", "active"),
        Output("link-states",    "active"),
        Output("link-help",      "active"),

        Output("link-overview",  "className"),
        Output("link-home",      "className"),
        Output("link-networks",  "className"),
        Output("link-countries", "className"),
        Output("link-states",    "className"),
        Output("link-help",      "className"),
    ],
    Input("url", "pathname"),
)
def highlight_active(pathname: str):
    is_overview  = pathname in ("/", "/overview")
    is_home      = bool(pathname and pathname.startswith("/home"))
    is_networks  = pathname == "/networks"
    is_countries = pathname == "/countries"
    is_states    = pathname == "/states"
    is_help      = pathname == "/help_guide"

    active_flags = [is_overview, is_home, is_networks, is_countries, is_states, is_help]

    def cls(active: bool) -> str:
        return "text-white bg-primary rounded" if active else "text-white"

    classes = [cls(f) for f in active_flags]
    return (*active_flags, *classes)

if __name__ == "__main__":
    app.run(debug=True)
