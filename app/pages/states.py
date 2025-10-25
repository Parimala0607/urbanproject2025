# pages/states.py
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import html, dcc, Input, Output, State, ctx, callback
import dash_bootstrap_components as dbc

from components import buttons, const, data_prep

# -------------------
# Data handles 
# -------------------
SUPPORTED_COUNTRIES = ["United States", "China", "India"]
FEATURE_ID = {"China": "properties.NAME_1", "India": "properties.st_nm"}

DF = data_prep.DF
STATS = data_prep.STATS
MEAN_DF = data_prep.MEAN_DF
GJSON = data_prep.GJSON


DF_V2 = getattr(data_prep, "DF_V2", DF)
STATS_V2 = getattr(data_prep, "STATS_V2", STATS)
MEAN_DF_V2 = getattr(data_prep, "MEAN_DF_V2", MEAN_DF)


def get_version_data(version: str, region: str):
    if version == "v1":
        return DF[region], STATS[region], MEAN_DF[region]
    return (
        DF_V2.get(region, DF[region]),
        STATS_V2.get(region, STATS[region]),
        MEAN_DF_V2.get(region, MEAN_DF[region]),
    )


def get_units(version: str, metric: str, pollutant: str):
    if version == "v1":
        return const.UNITS[metric][pollutant]
    return getattr(const, "UNITS_V2", const.UNITS)["Concentration"][pollutant]


def empty_fig(msg: str, ytitle: str = ""):
    fig = go.Figure()
    fig.update_layout(
        height=350,
        margin=dict(l=20, r=10, t=10, b=30),
        paper_bgcolor=const.DISP["background"],
        plot_bgcolor=const.DISP["background"],
        font=dict(size=const.FONTSIZE, family=const.FONTFAMILY),
        xaxis_title="",
        yaxis_title=ytitle,
    )
    fig.add_annotation(
        x=0.5, y=0.5, xref="paper", yref="paper",
        xanchor="center", yanchor="middle",
        showarrow=False, text=msg,
        font=dict(size=14, color="gray"),
    )
    return fig


# -------------------
# Layout 
# -------------------
layout = html.Div(
    [
        dbc.Card(
            dbc.CardBody(
                [
                    html.H2("Sub-national Level Summary", className="mb-1 text-center"),
                    html.P(
                        "Exploring urban pollutions averaged at the state- or province-level in the United States, China, and India.",
                        className="text-muted mb-4 text-center",
                    ),

                   
                    dbc.Card(
                        [
                            dbc.CardHeader("Filters", className="fw-semibold"),
                            dbc.CardBody(
                                [
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                html.Div(
                                                    [
                                                        html.Label("Data Version", className="form-label fw-semibold mb-1"),
                                                        buttons.data_version_toggle(id="states-data-version", value="v1"),
                                                    ]
                                                ),
                                                md=3,
                                            ),
                                            dbc.Col(
                                                html.Div(
                                                    [
                                                        html.Label("Pollutant Type", className="form-label fw-semibold mb-1"),
                                                        buttons.pollutant_type_dropdown(id="states-pollutant"),
                                                    ]
                                                ),
                                                md=3,
                                            ),
                                            dbc.Col(
                                                html.Div(
                                                    [
                                                        html.Label("Metric", className="form-label fw-semibold mb-1"),
                                                        buttons.metric_dropdown(id="states-metric"),
                                                    ]
                                                ),
                                                md=3,
                                            ),
                                            dbc.Col(
                                                html.Div(
                                                    [
                                                        html.Label("Country", className="form-label fw-semibold mb-1"),
                                                        dcc.Dropdown(
                                                            id="states-dd-country",
                                                            options=[{"label": c, "value": c} for c in SUPPORTED_COUNTRIES],
                                                            value="United States",
                                                            clearable=False,
                                                        ),
                                                    ]
                                                ),
                                                md=3,
                                            ),
                                        ],
                                        className="gy-3",
                                    ),
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                html.Div(
                                                    [
                                                        html.Label("State/Province", className="form-label fw-semibold mb-1"),
                                                        dcc.Dropdown(id="states-dd-state", options=[], value=None, clearable=False),
                                                    ]
                                                ),
                                                md=3,
                                            ),
                                            dbc.Col(
                                                html.Div(
                                                    [
                                                        html.Label("Year", className="form-label fw-semibold mb-1"),
                                                        buttons.year_dropdown(id="states-dd-year", start=2000, end=2020, value=2019),
                                                    ]
                                                ),
                                                md=3,
                                            ),
                                        ],
                                        className="gy-3 mt-1",
                                    ),
                                ]
                            ),
                        ],
                        className="mb-4",
                    ),

                   
                    dbc.Row(
                        [
                            
                            dbc.Col(
                                [
                                    html.H6(id="states-map-title", className="mb-2"),
                                    dcc.Graph(id="states-map", config={"displayModeBar": False}, style={"height": "480px"}),
                                    html.Div(
                                        [
                                            html.Span("Low", className="me-2"),
                                            html.Div(
                                                style={
                                                    "height": "10px",
                                                    "width": "120px",
                                                    "background": "linear-gradient(90deg, #2ecc71, #f1c40f, #e74c3c)",
                                                    "display": "inline-block",
                                                    "borderRadius": "6px",
                                                },
                                                className="me-2",
                                            ),
                                            html.Span("High", className="me-3"),
                                            html.Span("Color Scale: Green (low) → Red (high)", className="text-muted small"),
                                        ],
                                        className="mt-2",
                                    ),
                                ],
                                md=7,
                            ),

                            
                            dbc.Col(
                                [
                                    dbc.Card(
                                        dbc.CardBody(
                                            [
                                                html.H6(id="states-summary-title", className="mb-2"),

                                              
                                                html.Div(
                                                    [
                                                        html.Span("Select City", className="form-label fw-semibold small me-2"),
                                                        dcc.Dropdown(id="states-dd-city", options=[], value=None, clearable=False),
                                                    ],
                                                    className="mb-2",
                                                ),

                                                # Scatter
                                                dcc.Graph(
                                                    id="states-scatter",
                                                    config={"displayModeBar": False},
                                                    style={"height": "260px"},
                                                ),
                                                html.Div(
                                                    [
                                                        html.Span("X-axis scale:", className="small me-2"),
                                                        dcc.RadioItems(
                                                            id="states-scale",
                                                            value="linear",
                                                            options=[{"label": "Linear", "value": "linear"},
                                                                     {"label": "Log", "value": "log"}],
                                                            inputClassName="form-check-input me-1",
                                                            labelClassName="form-check-label me-3",
                                                            className="d-inline-flex align-items-center",
                                                        ),
                                                    ],
                                                    className="d-flex justify-content-center gap-3 mt-1 mb-2",
                                                ),

                                                # Trend
                                                dcc.Graph(
                                                    id="states-trend",
                                                    config={"displayModeBar": False},
                                                    style={"height": "260px"},
                                                ),

                                                html.Hr(className="my-3"),
                                                html.Div(id="states-city-stats", className="small text-muted"),
                                            ]
                                        ),
                                        className="shadow-sm",
                                    ),
                                ],
                                md=5,
                            ),
                        ],
                        className="gy-4",
                    ),
                ]
            ),
            className="content-card shadow-sm p-4",
        ),
        dcc.Store(id="states-store-version", data="v1"),
    ],
    className="states-page",
)

# -------------------
# Callbacks
# -------------------
@callback(
    Output("states-store-version", "data"),
    Output("states-data-version-v1", "color"),
    Output("states-data-version-v2", "color"),
    Input("states-data-version-v1", "n_clicks"),
    Input("states-data-version-v2", "n_clicks"),
    State("states-store-version", "data"),
)
def toggle_version(n1, n2, current):
    chosen = current
    if ctx.triggered_id == "states-data-version-v1":
        chosen = "v1"
    elif ctx.triggered_id == "states-data-version-v2":
        chosen = "v2"
    c1 = "primary" if chosen == "v1" else "secondary"
    c2 = "primary" if chosen == "v2" else "secondary"
    return chosen, c1, c2



@callback(
    Output("states-dd-state", "options"),
    Output("states-dd-state", "value"),
    Input("states-dd-country", "value"),
    Input("states-store-version", "data"),
)
def populate_states(country, version):
    df_cities, _, _ = get_version_data(version, country)
    if df_cities is None or "State" not in df_cities.columns:
        return [], None
    states = sorted(df_cities["State"].dropna().unique().tolist())
    return [{"label": s, "value": s} for s in states], (states[0] if states else None)



@callback(
    Output("states-dd-city", "options"),
    Output("states-dd-city", "value"),
    Input("states-dd-country", "value"),
    Input("states-dd-state", "value"),
    Input("states-store-version", "data"),
)
def populate_cities(country, state, version):
    df_cities, _, _ = get_version_data(version, country)
    if df_cities is None or not state:
        return [], None
    l = df_cities[df_cities["State"] == state]
    cities = sorted(l["CityID"].dropna().unique().tolist()) if not l.empty else []
    return [{"label": c, "value": c} for c in cities], (cities[0] if cities else None)



@callback(
    Output("states-metric", "options"),
    Output("states-pollutant", "options"),
    Input("states-pollutant", "value"),
    Input("states-metric", "value"),
    Input("states-store-version", "data"),
)
def enforce_metric_rules(selected_pollutant, selected_metric, version):
    metric_opts = buttons.metric_options(selected_pollutant == "CO2" or version == "v2")
    pol_opts = buttons.pol_options(selected_metric and selected_metric != "Concentration")
    return metric_opts, pol_opts



@callback(
    Output("states-map-title", "children"),
    Output("states-summary-title", "children"),
    Input("states-dd-country", "value"),
    Input("states-dd-state", "value"),
    Input("states-dd-city", "value"),
)
def update_titles(country, state, city):
    return (
        f"State/Province Pollution Map ({country})",
        f"Summary for {state} & {city}",
    )



@callback(
    Output("states-map", "figure"),
    Input("states-dd-country", "value"),
    Input("states-pollutant", "value"),
    Input("states-dd-year", "value"),
    Input("states-dd-state", "value"),
    Input("states-metric", "value"),
    Input("states-store-version", "data"),
)
def update_map(region, pollutant, year_value, state, metric, version):
    if version == "v2" and metric != "Concentration":
        metric = "Concentration"

    df_cities, stats_data, _ = get_version_data(version, region)
    if stats_data is None:
        return empty_fig("No stats for region")

    plot_column = data_prep.get_column_name("2" if version == "v2" else "1", metric, pollutant)
    m = stats_data["mean"].query("Year == @year_value").copy()
    if m.empty or plot_column not in m.columns:
        return empty_fig(f"No data for {year_value} / {plot_column}")

    st = m.query("State == @state") if state else m.iloc[0:0]

    if version == "v1" and "CO2" in plot_column:
        m["text"] = (
            "<b>" + m["State"] + "</b><br>" + get_units(version, metric, pollutant) + ": "
        ) + (m[plot_column].astype(float) / 1_000_000).round(3).astype(str) + "M"
        maxx = 7e6
    else:
        units_label = get_units(version, "Concentration" if version == "v2" else metric, pollutant)
        m["text"] = "<b>" + m["State"] + "</b><br>" + units_label + ": " + m[plot_column].round(2).astype(str)
        maxx = np.percentile(m[plot_column].dropna(), 90) if (version == "v2" and "CO2" in plot_column) else m[plot_column].max()

    if region == "United States":
        fig = go.Figure(
            data=go.Choropleth(
                locations=m["State"], locationmode="USA-states", customdata=m["State"],
                z=m[plot_column], hovertext=m["text"], hoverinfo="text",
                colorscale=const.CS[metric], zmin=0, zmax=maxx
            )
        )
        if not st.empty:
            fig.add_traces(
                data=go.Choropleth(
                    locations=st["State"], locationmode="USA-states",
                    z=st[plot_column], hoverinfo="skip",
                    colorscale=const.CS[metric], marker=dict(line_width=3), zmin=0, zmax=maxx
                )
            )
        fig.update_geos(scope="usa")
    else:
        fig = go.Figure(
            data=go.Choropleth(
                locations=m["State"], geojson=GJSON[region], z=m[plot_column],
                hovertext=m["text"], featureidkey=FEATURE_ID[region], hoverinfo="text",
                colorscale=const.CS[metric], zmin=0, zmax=maxx
            )
        )
        if not st.empty:
            fig.add_traces(
                data=go.Choropleth(
                    locations=st["State"], geojson=GJSON[region], featureidkey=FEATURE_ID[region],
                    z=st[plot_column], hoverinfo="skip",
                    colorscale=const.CS[metric], zmin=0, zmax=maxx, marker=dict(line_width=3)
                )
            )
        fig.update_geos(fitbounds="locations", visible=False)

    fig.update_layout(
        margin=dict(l=10, b=10, t=10, r=0), hovermode="closest",
        font=dict(size=const.FONTSIZE, family=const.FONTFAMILY),
        geo=dict(
            showland=True, landcolor=const.MAP_COLORS["lake"], coastlinewidth=0,
            oceancolor=const.MAP_COLORS["ocean"], subunitcolor="rgb(255,255,255)",
            countrycolor=const.MAP_COLORS["land"], countrywidth=0.5, showlakes=True,
            lakecolor=const.MAP_COLORS["ocean"], showocean=True, showcountries=True,
            resolution=50, bgcolor="#f5f5f5",
        ),
    )
    fig.update_traces(customdata=m["State"])
    return fig


# ---- Scatter (compact axes/legend, no extra headings) ----
@callback(
    Output("states-scatter", "figure"),
    Input("states-dd-country", "value"),
    Input("states-map", "hoverData"),
    Input("states-pollutant", "value"),
    Input("states-scale", "value"),
    Input("states-dd-year", "value"),
    Input("states-dd-state", "value"),
    Input("states-dd-city", "value"),
    Input("states-metric", "value"),
    Input("states-store-version", "data"),
)
def update_scatter(region, hoverData, pollutant, scale, year_value, stateS, cityS, metric, version):
    if version == "v2" and metric != "Concentration":
        metric = "Concentration"

    df_cities, _, _ = get_version_data(version, region)
    if df_cities is None:
        return empty_fig("No city dataframe", "")

    state_name = stateS
    if ctx.triggered_id == "states-map" and hoverData:
        state_name = hoverData["points"][0]["customdata"]

    dff = df_cities.query("State == @state_name and Year == @year_value")
    if dff.empty:
        return empty_fig("No rows for selection", "")

    plot_column = data_prep.get_column_name("2" if version == "v2" else "1", metric, pollutant)
    units_label = get_units(version, "Concentration" if version == "v2" else metric, pollutant)

    traces = []
    for i in const.COUNTRY_SCATTER:
        _c = dff.query("C40 == @i")
        if _c.empty:
            continue
        if version == "v1" and pollutant != "CO2" and metric != "Concentration":
            customdata = np.stack(
                (_c["CityID"], _c[pollutant],
                 _c.get(f"PAF_{pollutant}", np.zeros(len(_c))),
                 _c.get(f"Cases_{pollutant}", np.zeros(len(_c)))),
                axis=-1,
            )
            hover_template = (
                "<b>%{customdata[0]}</b><br>Population: %{x}<br>"
                f"{const.UNITS['Concentration'][pollutant]}: " + "%{customdata[1]}<br>"
                f"{const.UNITS['PAF'][pollutant]}: " + "%{customdata[2]}<br>"
                f"{const.UNITS['Cases'][pollutant]}: " + "%{customdata[3]}"
            )
        else:
            customdata = np.stack((_c["CityID"], _c[plot_column]), axis=-1)
            hover_template = (
                "<b>%{customdata[0]}</b><br>Population: %{x}<br>"
                f"{units_label}: " + "%{customdata[1]}<br>"
            )

        traces.append(
            go.Scatter(
                name=const.COUNTRY_SCATTER[i]["name"],
                x=_c["Population"], y=_c[plot_column],
                mode="markers", customdata=customdata, hovertemplate=hover_template,
                marker=dict(
                    color=const.COUNTRY_SCATTER[i]["color"],
                    symbol=const.COUNTRY_SCATTER[i]["symbol"],
                    size=8, line=dict(width=1, color=const.COUNTRY_SCATTER[i]["color"]),
                ),
            )
        )

    fig = go.Figure(traces)

    if cityS:
        sel = dff.query("CityID == @cityS")
        if not sel.empty:
            fig.add_trace(
                go.Scattergl(
                    mode="markers",
                    x=sel["Population"], y=sel[plot_column],
                    marker=dict(symbol="circle-open-dot", color="#FAED26", size=10, line=dict(width=2)),
                    showlegend=False, hoverinfo="skip",
                )
            )

    
    fig.update_xaxes(
    title="Population",
    type=("log" if scale == "log" else "linear"),
    showgrid=True,
    gridcolor="rgba(0,0,0,0.08)",
    zeroline=False,
    tickangle=0,  
    tickformat="~s",  
    showline=True,
    linecolor="rgba(0,0,0,0.3)",
    )
    fig.update_yaxes(
    title=(metric if metric != "Concentration" else units_label),
    showgrid=True,
    gridcolor="rgba(0,0,0,0.08)",
    zeroline=False,
    showline=True,
    linecolor="rgba(0,0,0,0.3)",
)
    fig.update_layout(
        height=260,
        margin=dict(l=40, b=50, t=5, r=10),
        hovermode="closest",
        legend_title_text="",
        legend=dict(orientation="h", yanchor="top", y=-0.25, xanchor="left", x=0.0),
        paper_bgcolor=const.DISP["background"],
        plot_bgcolor=const.DISP["background"],
        font=dict(size=const.FONTSIZE, family=const.FONTFAMILY),
    )
    return fig



def _build_state_trend_df(stats_data, state_value, plot_column):
    """Aligned Year/mean/min/max for the selected state."""
    mean_df = (
        stats_data["mean"]
        .loc[stats_data["mean"]["State"] == state_value, ["Year", plot_column]]
        .rename(columns={plot_column: "mean"})
    )
    min_df = (
        stats_data["min"]
        .loc[stats_data["min"]["State"] == state_value, ["Year", plot_column]]
        .rename(columns={plot_column: "min"})
    )
    max_df = (
        stats_data["max"]
        .loc[stats_data["max"]["State"] == state_value, ["Year", plot_column]]
        .rename(columns={plot_column: "max"})
    )
    out = mean_df.merge(min_df, on="Year", how="outer").merge(max_df, on="Year", how="outer")
    return out.sort_values("Year").reset_index(drop=True)


# ---- Trend (compact axes/legend) ----
@callback(
    Output("states-trend", "figure"),
    Output("states-city-stats", "children"),
    Input("states-dd-country", "value"),
    Input("states-scatter", "hoverData"),
    Input("states-pollutant", "value"),
    Input("states-dd-city", "value"),
    Input("states-dd-state", "value"),
    Input("states-metric", "value"),
    Input("states-store-version", "data"),
)
def update_trends(region, hover_city, pollutant, city_value, state_value, metric, version):
    if version == "v2" and metric != "Concentration":
        metric = "Concentration"

    df_cities, stats_data, _ = get_version_data(version, region)
    if df_cities is None or stats_data is None or not state_value:
        return empty_fig("Select a state"), [html.Div("—", className="text-muted")]


    city_sel = city_value
    if ctx.triggered_id == "states-scatter" and hover_city and "points" in hover_city:
        try:
            city_sel = hover_city["points"][0]["customdata"][0]
        except Exception:
            pass

    plot_column = data_prep.get_column_name("2" if version == "v2" else "1", metric, pollutant)

    
    state_trend = _build_state_trend_df(stats_data, state_value, plot_column)
    if state_trend.empty or state_trend["mean"].isna().all():
        return empty_fig(f"No trend data for {state_value}"), [html.Div("—", className="text-muted")]

    # city series
    city_rows = (
        df_cities.loc[df_cities["CityID"] == city_sel, ["Year", plot_column]]
        .sort_values("Year")
        .reset_index(drop=True)
    )
    city_years = city_rows["Year"] if not city_rows.empty else []
    city_vals = city_rows[plot_column] if not city_rows.empty else []

    dec = 0 if pollutant == "CO2" else 2
    if version == "v1":
        pcol = plot_column  
        units_label = const.UNITS[metric][pollutant]
    else:
        pcol = data_prep.V2_COLUMN_MAPPING.get(pollutant, pollutant + "_V2")
        units_label = getattr(const, "UNITS_V2", const.UNITS)["Concentration"][pollutant]

    fig = go.Figure(
        [
            go.Scatter(
                x=state_trend["Year"], y=state_trend["max"].round(decimals=dec),
                name="Maximum", marker={"color": "lightgray"}, line={"color": "lightgray"},
            ),
            go.Scatter(
                x=state_trend["Year"], y=state_trend["mean"].round(decimals=dec),
                name="Mean", marker={"color": "#4CB391"}, line={"color": "#4CB391"},
            ),
            go.Scatter(
                x=state_trend["Year"], y=state_trend["min"].round(decimals=dec),
                name="Minimum", marker={"color": "lightgray"}, line={"color": "lightgray"},
            ),
            go.Scatter(
                x=city_years, y=city_vals.round(decimals=dec),
                name="Selected city", marker={"color": "#CC5500"}, line={"color": "#CC5500"},
            ),
        ]
    )

    
    _, _, mean_df = get_version_data(version, region)
    if mean_df is not None and pcol in mean_df.columns:
        mean_sorted = mean_df[["Year", pcol]].sort_values("Year")
        fig.add_trace(
            go.Scatter(
                x=mean_sorted["Year"], y=mean_sorted[pcol].round(decimals=dec),
                name="Country mean", marker={"color": "black"},
                line={"color": "black", "dash": "dot"},
            )
        )

    fig.update_traces(mode="lines+markers", hovertemplate="%{y:,}")

  
    fig.update_xaxes(title="Year", showgrid=True, gridcolor="rgba(0,0,0,0.08)", zeroline=False)
    fig.update_yaxes(title=units_label, showgrid=True, gridcolor="rgba(0,0,0,0.08)", zeroline=False)
    fig.update_layout(
        hovermode="x unified",
        paper_bgcolor=const.DISP["background"],
        plot_bgcolor=const.DISP["background"],
        legend=dict(orientation="h", yanchor="top", y=-0.3, xanchor="left", x=0.0),
        height=260,
        margin=dict(l=45, b=55, r=10, t=5),
        font=dict(size=const.FONTSIZE, family=const.FONTFAMILY),
    )

    stats_panel = [
        html.Div("Selected City Details:", className="fw-semibold"),
        html.Div(f"City: {city_sel or '—'}"),
        html.Div(f"State: {state_value}"),
        html.Div(f"Pollutant: {pollutant}"),
        html.Div(f"Metric: {'Concentration' if version=='v2' else metric}"),
    ]
    return fig, stats_panel



@callback(
    Output("states-dd-state", "value", allow_duplicate=True),
    Input("states-dd-state", "value"),
    Input("states-map", "hoverData"),
    prevent_initial_call=True,
)
def sync_state_dropdown(state_sel, hoverData):
    if ctx.triggered_id == "states-map" and hoverData:
        return hoverData["points"][0]["customdata"]
    return state_sel
