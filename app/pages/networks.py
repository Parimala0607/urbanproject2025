# pages/networks.py
from dash import html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np


from components.buttons import pollutant_type_dropdown, metric_dropdown, year_dropdown 
from components import data_prep, const

DF = data_prep.DFILT.copy()


V2_COL = {"PM": "Pw_PM_V2", "NO2": "Pw_NO2_V2", "O3": "Pw_O3_V2", "CO2": "CO2_V2"}
V1_COL = {"PM": "Pw_PM",    "NO2": "Pw_NO2",    "O3": "Pw_O3",    "CO2": "CO2"}


MEM_COL = {
    "all": None,
    "c40": "C40",
    "gcom": "Global.Covenant.of.Mayors",
    "ccac": "CCAC",
}


_POL = {"pm":"PM","pm25":"PM","pm₂.₅":"PM","pm2.5":"PM",
        "no2":"NO2","no₂":"NO2","o3":"O3","o₃":"O3","co2":"CO2","co₂":"CO2"}
def _norm_pol(v): 
    if not v: return "PM"
    k = str(v).strip().lower()
    return _POL.get(k, "PM")

def _truthy(s: pd.Series) -> pd.Series:
    return s.astype(str).str.strip().str.lower().isin({"1","true","t","yes","y"})

def _ycol(version: str, pol_value: str, metric_value: str):
    pol = _norm_pol(pol_value)
    ver = (version or "v1").lower()
    met = (metric_value or "concentration").strip().lower()

    if ver == "v2":
        col = V2_COL[pol]
        title = const.UNITS_V2["Concentration"].get(pol, pol)
        return col, title


    if met == "concentration":
        col = V1_COL[pol]
        title = const.UNITS["Concentration"][pol]
    else:
       
        cap = metric_value.capitalize()
        col = f"{cap}_{pol}"
        title = cap
    return col, title

def _fallback_to_conc(df_slice: pd.DataFrame, version: str, pol: str, ycol: str):
    """If requested ycol missing/empty, fall back to concentration for same version+pollutant."""
    has = (ycol in df_slice.columns) and pd.to_numeric(df_slice[ycol], errors="coerce").notna().any()
    if has:
        return ycol, None
    polN = _norm_pol(pol)
    if (version or "v1").lower() == "v2":
        return V2_COL[polN], const.UNITS_V2["Concentration"].get(polN, polN)
    else:
        return V1_COL[polN], const.UNITS["Concentration"][polN]

# =======================
# Layout
# =======================
layout = html.Div([
    dbc.Card(dbc.CardBody([
        html.H2("Urban Climate Network Memberships", className="mb-1"),
        html.P("A closer look at cities in different urban climate networks",
               className="text-muted mb-4"),

        dbc.Card([
            dbc.CardHeader("Filters", className="fw-semibold"),
            dbc.CardBody([

                dbc.Row([
                    dbc.Col(html.Div([
                        html.Label("Data Version", className="form-label fw-semibold mb-1"),
                        dcc.RadioItems(
                            id="data-version",
                            options=[{"label": "Version 1", "value": "v1"},
                                     {"label": "Version 2", "value": "v2"}],
                            value="v1",
                            labelClassName="me-3",
                            inputClassName="me-1"
                        )
                    ]), md=4),

                    dbc.Col(html.Div([
                        html.Label("Pollutant Type", className="form-label fw-semibold mb-1"),
                        pollutant_type_dropdown(id="pollutant-type")  
                    ]), md=4),

                    dbc.Col(html.Div([
                        html.Label("Metric", className="form-label fw-semibold mb-1"),
                        metric_dropdown(id="metric")  
                    ]), md=4),
                ], className="gy-3"),

                dbc.Row([
                    dbc.Col(html.Div([
                        html.Label("Year", className="form-label fw-semibold mb-1"),
                        year_dropdown(id="dd-year",
                                      start=int(DF["Year"].min()),
                                      end=int(DF["Year"].max()),
                                      value=int(DF["Year"].min())),
                    ]), md=4),

                    dbc.Col(html.Div([
                        html.Label("Membership", className="form-label fw-semibold mb-1"),
                        dcc.Dropdown(
                            id="dd-membership",
                            options=[
                                {"label": "All Cities", "value": "all"},
                                {"label": "C40", "value": "c40"},
                                {"label": "GCoM", "value": "gcom"},
                                {"label": "CCAC", "value": "ccac"},
                            ],
                            value="all", clearable=False,
                        )
                    ]), md=4),
                ], className="gy-3 mt-1"),

                html.Div([
                    html.Label("Continents", className="form-label fw-semibold mb-2"),
                    dcc.Dropdown(
                        id="continents",
                        options=sorted(DF["continent"].dropna().astype(str).unique()),
                        value=sorted(DF["continent"].dropna().astype(str).unique()),
                        multi=True
                    )
                ], className="mt-2"),
            ])
        ], className="mb-4 networks-filters"),

        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H6("Urban Pollution vs. Population", className="mb-2"),
                    dcc.Graph(id="scatter-pop", config={"displayModeBar": False}),
                    html.Div([
                        html.Div("Population Scale:", className="me-2 fw-semibold small"),
                        dcc.RadioItems(
                            id="scale", value="linear",
                            options=[{"label": "Linear", "value": "linear"},
                                     {"label": "Log", "value": "log"}],
                            inputClassName="form-check-input me-1",
                            labelClassName="form-check-label me-3",
                            className="d-flex align-items-center"
                        )
                    ], className="d-flex align-items-center gap-3 mt-2"),
                    html.Small("X-axis: Population, Y-axis: pollutant metric (version-aware)",
                               className="text-muted graph-subtitle"),
                ], className="networks-graph"),
            ], md=7),

            dbc.Col([
                html.Div([
                    html.H6("Time-Series Trends for Selected City", className="mb-2"),
                    html.Div([
                        html.Span("Select City", className="form-label fw-semibold small me-2"),
                        dcc.Dropdown(
                            id="dd-city",
                            options=[{"label": v, "value": v} for v in sorted(DF["CityCountry"].unique())],
                            value=sorted(DF["CityCountry"].unique())[0],
                            clearable=False
                        )
                    ], className="mb-2"),

                    dcc.Graph(id="ts-pop", config={"displayModeBar": False}, className="mb-3"),
                    dcc.Graph(id="ts-pollutant", config={"displayModeBar": False}, className="mb-2"),
                    html.Div(id="city-stats", className="small text-muted")
                ], className="networks-graph"),
            ], md=5),
        ], className="gy-4"),

    ]), className="content-card shadow-sm p-4"),
], className="networks-page")


# =======================
# Callbacks 
# =======================


@callback(
    Output("scatter-pop", "figure"),
    Input("data-version", "value"),
    Input("pollutant-type", "value"),
    Input("metric", "value"),
    Input("dd-year", "value"),
    Input("continents", "value"),
    Input("dd-membership", "value"),
    Input("scale", "value"),
)
def draw_scatter(version, pollutant, metric, year, continents, membership_value, scale):
    dff = DF[DF["Year"] == year].copy()
    if continents:
        dff = dff[dff["continent"].astype(str).isin(continents)]

    mcol = MEM_COL.get((membership_value or "all").lower())
    if mcol and (mcol in dff.columns):
        dff = dff[_truthy(dff[mcol])]

    ycol, ytitle = _ycol(version, pollutant, metric)
    ycol, ytitle_fb = _fallback_to_conc(dff, version, pollutant, ycol)
    if ytitle_fb:
        ytitle = ytitle_fb

    dff["Population"] = pd.to_numeric(dff["Population"], errors="coerce")
    dff[ycol] = pd.to_numeric(dff[ycol], errors="coerce")
    dff = dff.dropna(subset=["Population", ycol])
    if scale == "log":
        dff = dff[dff["Population"] > 0]

    if dff.empty:
        fig = go.Figure()
        fig.update_layout(margin=dict(l=40, r=10, t=10, b=40))
        return fig

    fig = px.scatter(
        dff, x="Population", y=ycol, color="continent", hover_name="CityCountry",
        labels={"Population": "Population", ycol: ytitle, "continent": "Region"},
    )
    fig.update_layout(margin=dict(l=40, r=10, t=10, b=40), legend_title_text="")
    fig.update_xaxes(type="log" if scale == "log" else "linear")
    return fig



@callback(
    Output("ts-pop", "figure"),
    Output("ts-pollutant", "figure"),
    Output("city-stats", "children"),
    Input("dd-city", "value"),
    Input("data-version", "value"),
    Input("pollutant-type", "value"),
    Input("metric", "value"),
)
def draw_timeseries(city, version, pollutant, metric):
    dff = DF[DF["CityCountry"] == city].copy().sort_values("Year")
    if dff.empty:
        return go.Figure(), go.Figure(), [html.Div("No data for selected city.")]

    
    fig_pop = px.line(dff, x="Year", y="Population", markers=True,
                      labels={"Year": "Year", "Population": "Population"})
    fig_pop.update_layout(margin=dict(l=30, r=10, t=0, b=30))

    
    ycol, ytitle = _ycol(version, pollutant, metric)
    ycol, ytitle_fb = _fallback_to_conc(dff, version, pollutant, ycol)
    if ytitle_fb: ytitle = ytitle_fb

    if (ycol not in dff.columns) or pd.to_numeric(dff[ycol], errors="coerce").dropna().empty:
        fig_pol = go.Figure()
        fig_pol.update_layout(margin=dict(l=30, r=10, t=0, b=30))
    else:
        fig_pol = px.line(dff, x="Year", y=ycol, markers=True,
                          labels={"Year": "Year", ycol: ytitle})
        fig_pol.update_layout(margin=dict(l=30, r=10, t=0, b=30))

    last = dff.iloc[-1]
    stats = [
        html.Div("Selected City Data:", className="fw-semibold"),
        html.Div(f"City: {city}"),
        html.Div(f"Population ({int(last['Year'])}): {int(last['Population']):,}"),
    ]
    if ycol in dff.columns and pd.notna(last.get(ycol)):
        stats.append(html.Div(f"{ytitle} ({int(last['Year'])}): {last[ycol]}"))
    stats.append(html.Div(f"Region: {last.get('continent','NA')}"))
    return fig_pop, fig_pol, stats
