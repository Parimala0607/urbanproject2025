# pages/states.py
from dash import html, dcc, Input, Output, State, ctx
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

# Shared controls
from components.buttons import (
    data_version_toggle,
    pollutant_type_dropdown,
    metric_dropdown,
    country_dropdown,
    year_dropdown,
    state_dropdown,
    city_dropdown
)

countries = ['United States', 'China', 'India']

# -------------------
# Layout
# -------------------
layout = html.Div([
    dbc.Card(dbc.CardBody([

        html.H2("Sub-national Level Summary", className="mb-1 text-center"),
        html.P("Exploring urban pollutions averaged at the state- or province-level in the United States, China, and India.",
               className="text-muted mb-4 text-center"),

        # Filters
        dbc.Card([
            dbc.CardHeader("Filters", className="fw-semibold"),
            dbc.CardBody([

                dbc.Row([
                    dbc.Col(html.Div([
                        html.Label("Data Version", className="form-label fw-semibold mb-1"),
                        data_version_toggle(id="data-version", value="v1")
                    ]), md=3),

                    dbc.Col(html.Div([
                        html.Label("Pollutant Type", className="form-label fw-semibold mb-1"),
                        pollutant_type_dropdown(id="pollutant-type")
                    ]), md=3),

                    dbc.Col(html.Div([
                        html.Label("Metric", className="form-label fw-semibold mb-1"),
                        metric_dropdown(id="metric")
                    ]), md=3),

                    dbc.Col(html.Div([
                        html.Label("Country", className="form-label fw-semibold mb-1"),
                        country_dropdown(
                            id="dd-country",
                            options=[{"label": c, "value": c} for c in
                                     ["United States", "India", "China"]],
                            value="United States"
                        )
                    ]), md=3),
                ], className="gy-3"),

                dbc.Row([
                    dbc.Col(html.Div([
                        html.Label("State/Province", className="form-label fw-semibold mb-1"),
                        state_dropdown(
                            id="dd-state",
                            options=[],
                            value=None
                        )
                    ]), md=3),
                    dbc.Col(html.Div([
                        html.Label("Year", className="form-label fw-semibold mb-1"),
                        
                        year_dropdown(id="dd-year", 
                                       options=[],
                                       value=None
                        )
                    ]), md=3),
                ], className="gy-3 mt-1"),
            ])
        ], className="mb-4"),

        
        dbc.Row([

            # Left: Map placeholder
            dbc.Col([
                html.H6(id="map-title", className="mb-2"),
                html.Div(
                # "Map coming soon…", className="map-placeholder rounded"),
                dcc.Graph(
                    id='shaded-states',
                    hoverData={'points': [{'customdata': 'CA'}]},
                    config={
                        "modeBarButtonsToRemove": [
                        "zoom2d", "pan2d", "select2d", "lasso2d", "zoomIn2d", "zoomOut2d",
                        "autoScale2d", "resetScale2d", "hoverClosestCartesian",
                        "hoverCompareCartesian"
                    ],
                    "displaylogo": False
                    },
                    style={
                        "height": "100%",
                        "width": "100%",
                        "border": "none",
                        "outline": "none",
                        "backgroundColor": "#000000",
                        "boxShadow": "none", 
                    },
                    )
               ),
                html.Div([
                    html.Span("Low", className="me-2"),
                    html.Div(style={
                        "height": "10px", "width": "120px",
                        "background": "linear-gradient(90deg, #2ecc71, #f1c40f, #e74c3c)",
                        "display": "inline-block", "borderRadius": "6px"
                    }, className="me-2"),
                    html.Span("High", className="me-3"),
                    html.Span("Color Scale: Green (low) → Red (high)", className="text-muted small")
                ], className="mt-2"),
            ], md=7),

            # Right: Summary panel
            dbc.Col([
                dbc.Card(dbc.CardBody([
                    html.H6(id="summary-title", className="mb-2"),
                    html.Div([
                        html.Span("Select City", className="form-label fw-semibold small me-2"),
                        city_dropdown( 
                            id="dd-city",
                            options=[],
                            value=None
                        )
                    ], className="mb-2"),

                    html.Div([
                        html.Div("PM₂.₅ (µg/m³) vs Population Scatter Plot", className="small text-muted mb-1"),
                        dcc.Graph(id="city-scatter", config={"displayModeBar": False}),

                        html.Div([
                            html.Span("X-axis Scale:", className="small me-2"),
                            dcc.RadioItems(
                                id="scale", value="linear",
                                options=[{"label": "Linear", "value": "linear"},
                                         {"label": "Log", "value": "log"}],
                                inputClassName="form-check-input me-1",
                                labelClassName="form-check-label me-3",
                                className="d-flex align-items-center"
                            )
                        ], className="d-flex align-items-center gap-3"),
                        html.Div([
                            dbc.Badge("C40 Cities", color="primary", className="me-2"),
                            dbc.Badge("Others", color="secondary", className="me-2")
                        ], className="mt-2 mb-2"),
                    ]),

                    html.Div([
                        html.Div(id="trend-title", className="small text-muted mb-1"),
                        dcc.Graph(id="state-trend", config={"displayModeBar": False}),
                    ], className="mt-2"),

                    html.Hr(className="my-3"),
                    html.Div(id="city-stats", className="small text-muted"),
                ]), className="shadow-sm"),
            ], md=5),

        ], className="gy-4"),

    ]), className="content-card shadow-sm p-4"),

    dcc.Store(id="store-version", data="v1"),
], className="states-page")


# -------------------
# Callbacks
# -------------------
def register_callbacks(app):

    # -- Version Callback not needed as of now.
    # @app.callback(
    #     Output("store-version", "data"),
    #     Output("data-version-v1", "color"),
    #     Output("data-version-v2", "color"),
    #     Input("data-version-v1", "n_clicks"),
    #     Input("data-version-v2", "n_clicks"),
    #     State("store-version", "data"),
    #     prevent_initial_call=True,
    # )
    # def toggle_version(n1, n2, current):
    #     trig = ctx.triggered_id
    #     chosen = current
    #     if trig == "data-version-v1":
    #         chosen = "v1"
    #     elif trig == "data-version-v2":
    #         chosen = "v2"
    #     c1 = "primary" if chosen == "v1" else "secondary"
    #     c2 = "primary" if chosen == "v2" else "secondary"
    #     return chosen, c1, c2


    # Titles
    # @app.callback(
    #     Output("map-title", "children"),
    #     Output("summary-title", "children"),
    #     Output("trend-title", "children"),
    #     Input("dd-country", "value"),
    #     Input("dd-state", "value"),
    #     Input("dd-city", "value"),
    # )
    # def update_titles(country, state, city):
    #     city_label = {
    #         "la": "Los Angeles",
    #         "sf": "San Francisco",
    #         "mumbai": "Mumbai",
    #         "beijing": "Beijing",
    #     }.get(city, "Selected City")

    #     map_title = f"State/Province Pollution Map ({country})"
    #     summary_title = f"Summary for {state} & {city_label}, {state}"
    #     trend_title = f"Pollutant Trend for {city_label}, {state} (2000–2019)"
    #     return map_title, summary_title, trend_title

    
    @app.callback(
        Output("city-scatter", "figure"),
        Input("dd-country", "value"),
        Input("dd-state", "value"),
        Input("dd-city", "value"),
        Input("scale", "value"),
    )
    def update_city_scatter(country, state, city, scale):
        df = pd.DataFrame({
            "group": ["C40", "Other", "Other", "C40", "Other"],
            "population": [3_900_000, 880_000, 12_500_000, 21_000_000, 5_500_000],
            "pm25": [10.5, 9.5, 23.0, 82.0, 28.3],
            "label": ["LA","SF","Mumbai","Beijing","Other"]
        })
        fig = px.scatter(
            df, x="population", y="pm25", color="group", hover_name="label",
            labels=dict(population="Population", pm25="PM₂.₅ (µg/m³)")
        )
        fig.update_traces(marker=dict(size=10))
        fig.update_xaxes(type="log" if scale == "log" else "linear")
        fig.update_layout(margin=dict(l=30, r=10, t=0, b=30), legend_title_text="")
        return fig

    
    @app.callback(
        Output("state-trend", "figure"),
        Output("city-stats", "children"),
        Input("dd-country", "value"),
        Input("dd-state", "value"),
        Input("dd-city", "value"),
        Input("pollutant-type", "value"),
    )
    def update_state_trend(country, state, city, pollutant):
        years = [2000, 2005, 2010, 2015, 2019]
        df = pd.DataFrame({
            "year": years * 4,
            "value": [20,18,17,15,14,   14,13,12,11,10,   8,8,7,6,6,   12,11,10,9,10],
            "series": (["Max PM₂.₅"]*5 + ["Mean PM₂.₅"]*5 + ["Min PM₂.₅"]*5 + ["Selected City"]*5)
        })
        fig = px.line(df, x="year", y="value", color="series", markers=True,
                      labels=dict(year="Year", value="µg/m³"))
        fig.update_layout(margin=dict(l=30, r=10, t=0, b=30), legend_title_text="")

        stats = [
            html.Div("Selected City Details:", className="fw-semibold"),
            html.Div("Population: 3,900,000"),
            html.Div("PM₂.₅ (Current): 10.5 µg/m³"),
            html.Div("C40 City: Yes"),
        ]
        return fig, stats
