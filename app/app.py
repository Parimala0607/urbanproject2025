import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc

# Components
# from app import components
from components.sidebar import sidebar
from components.navbar import navbar
from components.footer import footer
from components.data_prep import STATES_DF
from components.data_prep import DF

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

# -- Help Page FAQs Toggles -- 

for i in range(len(help_guide.questions)):
    @app.callback(
        Output(f"collapse-{i}", "is_open"),
        Output(f"toggle-icon-{i}", "children"),
        Input(f"toggle-icon-{i}", "n_clicks"),
        State(f"collapse-{i}", "is_open"),
        prevent_initial_call=True,
    )
    def toggle_collapse(n, is_open, i=i):
        if n:
            new_state = not is_open
            return new_state, ("-" if new_state else "+")
        return is_open, "+"

# State page - Call backs
@app.callback(
    Output("dd-state", "options"),
    Output("dd-state", "value"),
    Input("dd-country", "value"),
    prevent_initial_call=False
    )
def filterStates(country):
    states= STATES_DF[country]['State'].fillna('').astype(str)
    filteredstates = sorted(states.unique())
    options = [{"label": s, "value": s} for s in filteredstates if s]
    first_value = options[0]["value"] if options else None
    return options, first_value

@app.callback(
    Output("dd-year", "options"),
    Output("dd-year", "value"),
    Input("dd-country", "value"),
    prevent_initial_call=False
    )
def filterYears(country):
    options = [{'label': str(year), 'value': year} for year in sorted(DF[country]['Year'].unique())]
    first_value = options[0]["value"] if options else None
    return options, first_value

@app.callback(
    Output("dd-city", "options"),
    Output("dd-city", "value"),
    Input("dd-country", "value"),
    Input("dd-state", "value"),
    prevent_initial_call=False
    )

def filterCities(country, state):
    df_data = DF[country]
    filteredState= df_data[df_data['State'] == state]
    options = [{'label': c, 'value': c} for c in sorted(filteredState["CityID"].unique())]
    first_value = options[0]["value"] if options else None
    return options, first_value


if __name__ == "__main__":
    app.run(debug=True)
