import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import numpy as np

# Components
# from app import components
from components.sidebar import sidebar
from components.navbar import navbar
from components.footer import footer
from components import data_prep, const
# from components.data_prep import STATES_DF
# from components.data_prep import DF
import plotly.express as px
import plotly.graph_objects as go

# Pages
from pages import (
    overview,
    home,
    networks,
    countries,
    states,
    help_guide,

)

STATES_DF = data_prep.STATES_DF
DF = data_prep.DF
c_gjson = data_prep.GJSON
feature_id = {'China': 'properties.NAME_1', 'India': 'properties.st_nm'}

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

@app.callback(
    Output('shaded-states', 'figure'),
    [Input('dd-country', 'value'),
     Input('pollutant-type', 'value'),
     Input('dd-year', 'value'),
     Input('dd-state', 'value'),
     Input('metric', 'value'),
    #  Input('state-version-store', 'data')
     ]
)
def update_map(country, pollutant, year_value, state, metric):
    # Force 'Concentration' metric for Version 2 (as it doesn't have health metrics)
    # if version == '2' and metric != 'Concentration':
    #     metric = 'Concentration'
    version = '1'
    # Get plot column based on version
    plot_column = data_prep.get_column_name(version, metric, pollutant)
    
    # Get data for selected year
    df_data = DF[country]
    stats_data = data_prep.STATS[country]
    m = stats_data['mean'].query('Year == @year_value').copy()
    st = m.query('State == @state')
    
    unit_s = pollutant
    
    # Set appropriate units and formatting based on version
    if version == '1':
        # Version 1 formatting
        if 'CO2' in plot_column:
            if 'w_' in plot_column:  # We're not using this anymore but kept for compatibility
                maxx = 50e6
            else:
                maxx = 7e6
            m['text'] = '<b>' + m['State'] + '</b><br>' + const.UNITS[metric][unit_s] + ': ' + \
                        round((m[plot_column].astype(float) / 1000000), 3).astype(str) + 'M'
        else:
            m['text'] = '<b>' + m['State'] + '</b><br>' + const.UNITS[metric][unit_s] + ': ' + \
                        m[plot_column].round(2).astype(str)
            if plot_column == 'Cases_NO2':
                maxx = 1980
            elif plot_column == 'Cases_PM':
                maxx = 250
            elif plot_column == 'Cases_O3':
                maxx = 110
            else:
                maxx = m[plot_column].max()
    else:
        # Version 2 formatting (similar to countries.py)
        units_label = const.UNITS_V2['Concentration'][unit_s] if hasattr(const, 'UNITS_V2') else const.UNITS['Concentration'][unit_s]
        
        if 'CO2' in plot_column:
            m['text'] = '<b>' + m['State'] + '</b><br>' + units_label + ': ' + \
                        m[plot_column].round(2).astype(str)
            maxx = np.percentile(m[plot_column].dropna(), 90)  # 90th percentile
        else:
            m['text'] = '<b>' + m['State'] + '</b><br>' + units_label + ': ' + \
                        m[plot_column].round(2).astype(str)
            maxx = m[plot_column].max()
    
    # Create choropleth map
    if country == 'United States':  #No outside geojson for USA so plot with plotly's internal USA-states locations
        fig = go.Figure(data=go.Choropleth(
            locations=m['State'], locationmode='USA-states', customdata=m['State'],
            z=m[plot_column], hovertext=m['text'], hoverinfo='text',
            colorscale=const.CS[metric], zmin=0, zmax=maxx, 
            showscale=False
        ))
        fig.add_traces(data=go.Choropleth(
            locations=st['State'], locationmode='USA-states',
            z=st[plot_column], hoverinfo='skip',
            colorscale=const.CS[metric],
            marker=dict(line_width=3), zmin=0, zmax=maxx, 
            showscale=False
        ))
        fig.update_geos(scope='usa')
        
    else:  ##Use the uploaded geojson files for China and India states
        fig = go.Figure(data=go.Choropleth(
            locations=m["State"], geojson=c_gjson[country], z=m[plot_column],
            hovertext=m['text'], featureidkey=feature_id[country], hoverinfo='text',
            colorscale=const.CS[metric], zmin=0, zmax=maxx,
            showscale=False
        ))
        fig.add_traces(data=go.Choropleth(
            locations=st['State'], geojson=c_gjson[country], featureidkey=feature_id[country],
            z=st[plot_column], hoverinfo='skip',
            colorscale=const.CS[metric], zmin=0, zmax=maxx,
            marker=dict(line_width=3),
            showscale=False
        ))
        fig.update_geos(fitbounds='locations', visible=False)
    
    fig.update_layout(
        legend_title_text='',
        margin={'l': 10, 'b': 10, 't': 10, 'r': 0},
        hovermode='closest',
        font=dict(
            size=const.FONTSIZE,
            family=const.FONTFAMILY
        ),
        geo=dict(
            showland=True,
            landcolor=const.MAP_COLORS['lake'],
            coastlinewidth=0,
            oceancolor=const.MAP_COLORS['ocean'],
            subunitcolor="rgb(255, 255, 255)",
            countrycolor=const.MAP_COLORS['land'],
            countrywidth=0.5,
            showlakes=True,
            lakecolor=const.MAP_COLORS['ocean'],
            showocean=True,
            showcountries=True,
            resolution=50,
            bgcolor='#f5f5f5'
        ),
    )
    fig.update_traces(customdata=m['State'])
    fig.update_yaxes(title=plot_column)
    
    return fig

if __name__ == "__main__":
    app.run(debug=True)
