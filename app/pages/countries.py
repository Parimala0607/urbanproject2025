# pages/countries.py
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import html, dcc, Input, Output, State, ctx, callback, no_update
import dash_bootstrap_components as dbc

from components import buttons, const, data_prep

# =========================
# Data handles
# =========================
DFILT          = data_prep.DFILT
MEAN, MAX, MIN = data_prep.MEAN, data_prep.MAX, data_prep.MIN
DFILT_V2       = getattr(data_prep, "DFILT_V2", data_prep.DFILT)
MEAN_V2        = getattr(data_prep, "MEAN_V2",  data_prep.MEAN)
MAX_V2         = getattr(data_prep, "MAX_V2",   data_prep.MAX)
MIN_V2         = getattr(data_prep, "MIN_V2",   data_prep.MIN)

def get_version_data(version: str):
    return (DFILT_V2, MEAN_V2, MAX_V2, MIN_V2) if version == "v2" else (DFILT, MEAN, MAX, MIN)


def norm_pollutant(v: str) -> str:
    if v in {"PM", "NO2", "O3", "CO2"}:
        return v
    return {"pm25": "PM", "no2": "NO2", "o3": "O3", "co2": "CO2"}.get(v, "PM")

def norm_metric(v: str) -> str:
    if v in {"Concentration", "PAF", "Cases", "Rates"}:
        return v
    return {
        "concentration": "Concentration",
        "paf": "PAF",
        "cases": "Cases",
        "rate": "Rates",
        "rates": "Rates",
    }.get(v, "Concentration")


def _apply_card_style(fig, *, legend_bottom=True):
    fig.update_layout(
        autosize=True,
        paper_bgcolor="#f6f9ff",
        plot_bgcolor="#f6f9ff",
        margin=dict(l=40, r=30, t=36, b=64),
        font=dict(size=13, family=const.FONTFAMILY, color="#1b1b1b"),
        hovermode="closest",
    )
    fig.update_xaxes(
        showgrid=True, gridcolor="rgba(0,0,0,.08)", zeroline=False,
        linecolor="rgba(0,0,0,.35)", linewidth=1,
        ticks="outside", ticklen=5, tickwidth=1,
        title_font=dict(size=16), tickfont=dict(size=12)
    )
    fig.update_yaxes(
        showgrid=True, gridcolor="rgba(0,0,0,.08)", zeroline=False,
        linecolor="rgba(0,0,0,.35)", linewidth=1,
        ticks="outside", ticklen=5, tickwidth=1,
        title_font=dict(size=16), tickfont=dict(size=12)
    )
    if legend_bottom:
        fig.update_layout(
            legend=dict(orientation="h", x=0, y=-0.22, bgcolor="rgba(255,255,255,0)"),
            legend_title_text=""
        )
    return fig


POP_LOG_TICKVALS = [1, 10, 100, 1_000, 10_000, 100_000, 1_000_000, 10_000_000, 100_000_000]
POP_LOG_TICKTEXT = ["1", "10", "100", "1k", "10k", "100k", "1M", "10M", "100M"]

def _format_population_axis(fig, axis="x", scale="linear"):
    if scale == "log":
        fig.update_layout(**{f"{axis}axis_type": "log"})
        fig.update_layout(**{
            f"{axis}axis": dict(
                tickmode="array",
                tickvals=POP_LOG_TICKVALS,
                ticktext=POP_LOG_TICKTEXT,
                ticks="outside", ticklen=5, tickwidth=1,
                title="Population",
            )
        })
    else:
        fig.update_layout(**{f"{axis}axis_type": "linear"})
        fig.update_layout(**{
            f"{axis}axis": dict(
                tickformat="~s",
                ticks="outside", ticklen=5, tickwidth=1,
                title="Population",
            )
        })

def _format_pm25_axis(fig, axis="y", rng=None, dtick=50, units_label="PM₂.₅ (µg/m³)"):
    upd = {f"{axis}axis": dict(
        title=units_label,
        ticks="outside", ticklen=5, tickwidth=1,
        showgrid=True, gridcolor="rgba(0,0,0,.08)",
        zeroline=False, linecolor="rgba(0,0,0,.35)", linewidth=1,
        title_font=dict(size=16), tickfont=dict(size=12)
    )}
    if rng:
        upd[f"{axis}axis"]["range"] = list(rng)
        upd[f"{axis}axis"]["dtick"] = dtick
    fig.update_layout(**upd)

def _fixed_pm25_range_scatter(series):
    arr = np.asarray(series, dtype=float)
    if arr.size == 0 or np.all(np.isnan(arr)):
        return (0, 155), 50
    mx = float(np.nanmax(arr))
    upper = 100 if mx <= 100 else 150
    return (0, upper + 5), 50

def _empty_fig(msg: str):
    fig = go.Figure()
    _apply_card_style(fig)
    fig.add_annotation(x=0.5, y=0.5, xref="paper", yref="paper",
                       xanchor="center", yanchor="middle",
                       showarrow=False, text=msg, font=dict(size=14, color="gray"))
    return fig

# =========================
# Layout
# =========================
layout = html.Div(
    [
        dbc.Card(
            dbc.CardBody(
                [
                    html.H2("Countrywide Summary", className="mb-1 text-center"),
                    html.P("Exploring urban pollutions averaged at the country-level",
                           className="text-muted mb-4 text-center"),

                    # Filters
                    dbc.Card(
                        [
                            dbc.CardHeader("Filters", className="fw-semibold"),
                            dbc.CardBody(
                                [
                                    dbc.Row(
                                        [
                                            dbc.Col(buttons.data_version_toggle(
                                                id="data-version-countries", value="v1"), md=3),
                                            dbc.Col(buttons.pollutant_type_dropdown(
                                                id="pollutant-type-countries"), md=3),
                                            dbc.Col(buttons.metric_dropdown(
                                                id="metric-countries"), md=3),
                                            dbc.Col(buttons.country_dropdown(
                                                id="dd-country-countries",
                                                options=[{"label": c, "value": c}
                                                         for c in sorted(DFILT["Country"].dropna().unique())],
                                                value=("United States" if "United States" in DFILT["Country"].unique()
                                                       else DFILT["Country"].dropna().iloc[0]),
                                            ), md=3),
                                        ],
                                        className="gy-3",
                                    ),
                                    dbc.Row(
                                        [
                                            dbc.Col(buttons.year_dropdown(
                                                id="dd-year-countries",
                                                start=int(DFILT["Year"].min()),
                                                end=int(DFILT["Year"].max()),
                                                value=2019 if 2019 in DFILT["Year"].astype(int).unique()
                                                else int(DFILT["Year"].max()),
                                            ), md=3),
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
                            # Map
                            dbc.Col(
                                [
                                    html.H6("Country Pollution Map", className="mb-2"),
                                    dcc.Graph(
                                        id="shaded-map-countries",
                                        responsive=True,
                                        config={"displayModeBar": False},
                                        style={"width": "100%", "height": "500px",
                                               "border": "none", "backgroundColor": "transparent"},
                                    ),
                                    html.Div([
                                        html.Span("Low", className="me-2"),
                                        html.Div(style={
                                            "height": "10px", "width": "120px",
                                            "background": "linear-gradient(90deg, #2ecc71, #f1c40f, #e74c3c)",
                                            "display": "inline-block", "borderRadius": "6px"
                                        }, className="me-2"),
                                        html.Span("High", className="me-3"),
                                        html.Span("Color Scale: Green (low) → Red (high)",
                                                  className="text-muted small")
                                    ], className="mt-2"),
                                ],
                                md=7,
                            ),

                            # Right panel
                            dbc.Col(
                                [
                                    dbc.Card(
                                        dbc.CardBody(
                                            [
                                                html.H6(id="summary-title-countries", className="mb-2"),
                                                html.Div([
                                                    html.Span("Select City",
                                                              className="form-label fw-semibold small me-2"),
                                                    buttons.city_dropdown(
                                                        id="dd-city-countries", options=[], value=None),
                                                ], className="mb-2"),

                                                html.Div([
                                                    html.Div("PM₂.₅ (µg/m³) vs Population Scatter Plot",
                                                             className="small text-muted mb-1"),
                                                    dcc.Graph(
                                                        id="cities-scatter-countries",
                                                        responsive=True,
                                                        config={"displayModeBar": False},
                                                        style={"width": "100%", "height": "380px",
                                                               "border": "none", "backgroundColor": "transparent"},
                                                    ),
                                                    html.Div(
                                                        [
                                                            html.Span("X-axis scale:", className="fw-semibold me-2"),
                                                            html.Div([
                                                                dbc.Button("Linear", id="xscale-linear",
                                                                           color="primary", className="me-2",
                                                                           n_clicks=0),
                                                                dbc.Button("Log", id="xscale-log",
                                                                           color="secondary", n_clicks=0),
                                                            ], className="d-inline-flex"),
                                                        ],
                                                        className="d-flex align-items-center mt-2"
                                                    ),
                                                ]),

                                                html.Div([
                                                    html.Div("PM₂.₅ – Trends (2000–2019)",
                                                             className="small text-muted mb-1"),
                                                    dcc.Graph(
                                                        id="country-trends-graph-countries",
                                                        responsive=True,
                                                        config={"displayModeBar": False},
                                                        style={"width": "100%", "height": "380px",
                                                               "border": "none", "backgroundColor": "transparent"},
                                                    ),
                                                ], className="mt-2"),

                                                html.Hr(className="my-3"),
                                                html.Div(id="city-stats-countries", className="small text-muted"),
                                            ]
                                        ),
                                        className="shadow-sm",
                                    )
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

        dcc.Store(id="store-version-countries", data="v1"),
        dcc.Store(id="crossfilter-xaxis-typecountry", data="Linear"),
    ],
    className="countries-page",
)

# =========================
# Callbacks
# =========================
@callback(
    Output("store-version-countries", "data"),
    Output("data-version-countries-v1", "color"),
    Output("data-version-countries-v2", "color"),
    Input("data-version-countries-v1", "n_clicks"),
    Input("data-version-countries-v2", "n_clicks"),
    State("store-version-countries", "data"),
    prevent_initial_call=True,
)
def toggle_version(n1, n2, current):
    trig = ctx.triggered_id
    chosen = "v1" if trig == "data-version-countries-v1" else ("v2" if trig == "data-version-countries-v2" else current)
    return chosen, ("primary" if chosen == "v1" else "secondary"), ("primary" if chosen == "v2" else "secondary")


@callback(
    Output("crossfilter-xaxis-typecountry", "data"),
    Output("xscale-linear", "color"),
    Output("xscale-log", "color"),
    Input("xscale-linear", "n_clicks"),
    Input("xscale-log", "n_clicks"),
    prevent_initial_call=True,
)
def toggle_xscale(n1, n2):
    trig = ctx.triggered_id
    if trig == "xscale-linear":
        return "Linear", "primary", "secondary"
    if trig == "xscale-log":
        return "Log", "secondary", "primary"
    return no_update, no_update, no_update

@callback(
    Output("metric-countries", "options"),
    Output("metric-countries", "value"),
    Input("pollutant-type-countries", "value"),
    Input("store-version-countries", "data"),
    State("metric-countries", "value"),
)
def guard_metrics_for_co2_v2(pollutant_value, version, current_metric):
    pol_up = norm_pollutant(pollutant_value)
    if pol_up == "CO2" or version == "v2":
        opts = [
            {"label": "Concentration", "value": "concentration"},
            {"label": "PAF",           "value": "paf",   "disabled": True},
            {"label": "Cases",         "value": "cases", "disabled": True},
            {"label": "Rate",          "value": "rate",  "disabled": True},
        ]
        return opts, "concentration"
    opts = buttons.metric_dropdown(id="metric-countries").options
    return opts, (current_metric or "concentration")

@callback(
    Output("summary-title-countries", "children"),
    Input("dd-country-countries", "value"),
    Input("dd-city-countries", "value"),
)
def update_summary_title(country, city):
    return f"Summary for {country or 'Selected Country'} & {city or 'Selected City'}"

@callback(
    Output("dd-city-countries", "options"),
    Output("dd-city-countries", "value"),
    Input("dd-country-countries", "value"),
    Input("store-version-countries", "data"),
)
def update_city_dropdown(country, version):
    DF, *_ = get_version_data(version)
    if not country:
        return [], None
    dff = DF.query("Country == @country")
    cities = sorted(dff["CityCountry"].dropna().unique())
    return [{"label": c, "value": c} for c in cities], (cities[0] if cities else None)

@callback(
    Output("dd-country-countries", "value"),
    Input("dd-country-countries", "value"),
    Input("shaded-map-countries", "hoverData"),
)
def sync_country_hover(current_country, hover):
    if ctx.triggered_id == "shaded-map-countries" and hover and hover.get("points"):
        return hover["points"][0].get("customdata", current_country)
    return current_country

# -------- Map --------
@callback(
    Output("shaded-map-countries", "figure"),
    Input("pollutant-type-countries", "value"),
    Input("dd-year-countries", "value"),
    Input("dd-country-countries", "value"),
    Input("metric-countries", "value"),
    Input("store-version-countries", "data"),
)
def update_map(pollutant_value, year_value, countryS, metric_value, version):
    DF_V, MEAN_V, MAX_V, MIN_V = get_version_data(version)
    pollutant = norm_pollutant(pollutant_value)
    metric    = "Concentration" if version == "v2" else norm_metric(metric_value)
    plot_column = data_prep.get_column_name("2" if version == "v2" else "1", metric, pollutant)

    m = MEAN_V.query("Year == @year_value").copy()
    if m.empty or plot_column not in m.columns:
        return _empty_fig("No data for selected filters")

   
    vals = pd.to_numeric(m[plot_column], errors="coerce")
    if version == "v1":
        if "CO2" in plot_column:
            maxx = 4e6
            text = ("<b>"+m["Country"]+"</b><br>"
                    + const.UNITS["Concentration"][pollutant]+": "
                    + (vals/1_000_000).round(3).astype(str) + "M")
        else:
            text = ("<b>"+m["Country"]+"</b><br>"
                    + const.UNITS[metric][pollutant]+": "+ vals.round(2).astype(str))
            maxx = 500 if plot_column == "Cases_NO2" else (300 if plot_column == "Cases_PM" else vals.max())
    else:
        text = ("<b>"+m["Country"]+"</b><br>"
                + const.UNITS_V2["Concentration"][pollutant]+": "+ vals.round(2).astype(str))
        maxx = np.percentile(vals.dropna(), 90) if plot_column == "CO2_V2" else vals.max()

    fig = go.Figure(go.Choropleth(
        locations=m["Country"], locationmode="country names",
        customdata=m["Country"], z=vals, hovertext=text, hoverinfo="text",
        colorscale=const.CS[metric], zmin=0, zmax=maxx
    ))

    ctry = m.query("Country == @countryS")
    if not ctry.empty:
        fig.add_traces(go.Choropleth(
            locations=ctry["Country"], locationmode="country names",
            z=pd.to_numeric(ctry[plot_column], errors="coerce"), hoverinfo="skip",
            colorscale=const.CS[metric], zmin=0, zmax=maxx,
            marker=dict(line=dict(width=2.3, color="#3d3d3d"))
        ))

    fig.update_geos(showframe=False)
    fig.update_layout(
        autosize=True,
        legend_title_text="",
        paper_bgcolor=const.DISP["background"],
        plot_bgcolor=const.DISP["background"],
        margin={"l":10,"b":10,"t":10,"r":0},
        hovermode="closest",
        height=500,
        geo=dict(
            showland=True, landcolor=const.MAP_COLORS["lake"], coastlinewidth=0,
            oceancolor=const.MAP_COLORS["ocean"], subunitcolor="rgb(255,255,255)",
            countrycolor=const.MAP_COLORS["land"], countrywidth=0.5,
            showlakes=True, lakecolor=const.MAP_COLORS["ocean"],
            showocean=True, showcountries=True, resolution=50,
        ),
        font=dict(size=const.FONTSIZE, family=const.FONTFAMILY),
    )
    return fig

# -------- Scatter --------
@callback(
    Output("cities-scatter-countries", "figure"),
    Input("shaded-map-countries", "hoverData"),
    Input("pollutant-type-countries", "value"),
    Input("crossfilter-xaxis-typecountry", "data"),
    Input("dd-year-countries", "value"),
    Input("dd-country-countries", "value"),
    Input("dd-city-countries", "value"),
    Input("metric-countries", "value"),
    Input("store-version-countries", "data"),
)
def update_scatter(hoverData, pollutant_value, xaxis_type, year_value, countryS, cityS, metric_value, version):
    DF_V, *_ = get_version_data(version)
    pollutant = norm_pollutant(pollutant_value)
    metric    = "Concentration" if version == "v2" else norm_metric(metric_value)
    plot_column = data_prep.get_column_name("2" if version == "v2" else "1", metric, pollutant)

    country_name = (hoverData["points"][0]["customdata"]
                    if ctx.triggered_id == "shaded-map-countries" and hoverData and hoverData.get("points")
                    else countryS)

    dff = DF_V[(DF_V["Country"] == country_name) & (DF_V["Year"] == year_value)].copy()
    if dff.empty or plot_column not in dff.columns:
        return _empty_fig("No cities for the selected filters")

    
    dff["Population"] = pd.to_numeric(dff["Population"], errors="coerce")
    dff[plot_column]  = pd.to_numeric(dff[plot_column],  errors="coerce")
    dff = dff.dropna(subset=["Population", plot_column])

    city_df = dff[dff["CityCountry"] == (cityS or "")]

    traces = []
    for mem in const.COUNTRY_SCATTER:
        _c = dff.query("C40 == @mem")
        if _c.empty:
            continue

        if version == "v1" and metric != "Concentration":
            customdata = np.stack((_c["CityCountry"], _c.get(pollutant, _c[plot_column]),
                                   _c.get(f"PAF_{pollutant}", np.zeros(len(_c))),
                                   _c.get(f"Cases_{pollutant}", np.zeros(len(_c)))), axis=-1)
            hovertemplate = (
                "<b>%{customdata[0]}</b><br>"
                "Population: %{x}<br>"
                f"{const.UNITS['Concentration'][pollutant]}: " + "%{customdata[1]}<br>"
                f"{const.UNITS['PAF'][pollutant]}: " + "%{customdata[2]}<br>"
                f"{const.UNITS['Cases'][pollutant]}: " + "%{customdata[3]}"
            )
        else:
            customdata = np.stack((_c["CityCountry"], _c[plot_column]), axis=-1)
            units = const.UNITS["Concentration"][pollutant] if version == "v1" \
                    else const.UNITS_V2["Concentration"][pollutant]
            hovertemplate = (
                "<b>%{customdata[0]}</b><br>"
                "Population: %{x}<br>"
                f"{units}: " + "%{customdata[1]}<br>"
            )

        traces.append(go.Scatter(
            name=const.COUNTRY_SCATTER[mem]["name"],
            x=_c["Population"], y=_c[plot_column], mode="markers",
            customdata=customdata, hovertemplate=hovertemplate,
            marker={"color": const.COUNTRY_SCATTER[mem]["color"],
                    "symbol": const.COUNTRY_SCATTER[mem]["symbol"],
                    "line": dict(width=1, color=const.COUNTRY_SCATTER[mem]["color"]),
                    "size": 9, "opacity": 0.95}
        ))

    fig = go.Figure(traces)

    if not city_df.empty:
        fig.add_trace(go.Scattergl(
            mode="markers",
            x=city_df["Population"], y=city_df[plot_column],
            customdata=np.stack((city_df["CityCountry"], city_df[plot_column]), axis=-1),
            opacity=1, marker=dict(symbol="circle-open-dot", color="#FAED26", size=11, line=dict(width=2)),
            showlegend=False, hoverinfo="skip",
        ))

    _format_population_axis(fig, axis="x", scale=("log" if xaxis_type == "Log" else "linear"))

    if pollutant == "PM":
        rng, dtick = _fixed_pm25_range_scatter(dff[plot_column].to_numpy())
        _format_pm25_axis(fig, axis="y", rng=rng, dtick=dtick, units_label="PM₂.₅ (µg/m³)")
    else:
        _format_pm25_axis(fig, axis="y", rng=None,
                          units_label=(const.UNITS["Concentration"].get(pollutant, "Value")))

    _apply_card_style(fig, legend_bottom=True)
    fig.add_annotation(
        x=0, y=1.02, xanchor="left", yanchor="bottom",
        xref="paper", yref="paper", showarrow=False,
        text=f"<b>{country_name}</b>", font=dict(size=14),
        bgcolor="rgba(255,255,255,0)"
    )
    return fig

# -------- Trends --------
@callback(
    Output("country-trends-graph-countries", "figure"),
    Output("city-stats-countries", "children"),
    Input("cities-scatter-countries", "hoverData"),
    Input("dd-country-countries", "value"),
    Input("pollutant-type-countries", "value"),
    Input("dd-city-countries", "value"),
    Input("metric-countries", "value"),
    Input("store-version-countries", "data"),
)
def update_timeseries(cityHover, country_name, pollutant_value, cityS, metric_value, version):
    DF_V, *_ = get_version_data(version)

    pollutant = norm_pollutant(pollutant_value)
    metric    = "Concentration" if version == "v2" else norm_metric(metric_value)
    plot_col  = data_prep.get_column_name("2" if version == "v2" else "1", metric, pollutant)

    
    if ctx.triggered_id == "cities-scatter-countries" and cityHover and cityHover.get("points"):
        cd = cityHover["points"][0].get("customdata")
        city_sel = cd[0] if isinstance(cd, (list, np.ndarray)) else cityS
    else:
        city_sel = cityS

    
    dff = DF_V.loc[DF_V["Country"] == country_name, ["Year", plot_col]].copy()
    dff["Year"] = pd.to_numeric(dff["Year"], errors="coerce")
    dff[plot_col] = pd.to_numeric(dff[plot_col], errors="coerce")
    dff = dff.dropna()

    if dff.empty:
        return _empty_fig("No trend data"), [
            html.Div("Selected City Details:", className="fw-semibold"),
            html.Div(f"City: {city_sel or '—'}"),
            html.Div(f"Country: {country_name or '—'}"),
            html.Div(f"Metric: {metric}"),
        ]

    agg = (dff.groupby("Year")[plot_col]
             .agg(Mean="mean", Minimum="min", Maximum="max")
             .reset_index()
             .sort_values("Year"))

    
    city_series = DF_V.loc[DF_V["CityCountry"] == (city_sel or ""), ["Year", plot_col]].copy()
    if not city_series.empty:
        city_series["Year"] = pd.to_numeric(city_series["Year"], errors="coerce")
        city_series[plot_col] = pd.to_numeric(city_series[plot_col], errors="coerce")
        city_series = city_series.dropna().sort_values("Year")

    # --- figure ---
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=agg["Year"], y=agg["Maximum"], name="Maximum",
                             line={"color":"rgba(0,0,0,0.35)", "dash":"dash"},
                             marker={"color":"rgba(0,0,0,0.35)", "size":7}))
    fig.add_trace(go.Scatter(x=agg["Year"], y=agg["Mean"], name="Mean",
                             line={"color":"#4CB391", "width":2},
                             marker={"color":"#4CB391", "size":7}))
    fig.add_trace(go.Scatter(x=agg["Year"], y=agg["Minimum"], name="Minimum",
                             line={"color":"rgba(0,0,0,0.25)", "dash":"dot"},
                             marker={"color":"rgba(0,0,0,0.25)", "size":7}))
    if not city_series.empty:
        fig.add_trace(go.Scatter(x=city_series["Year"], y=city_series[plot_col].round(2),
                                 name="Selected city",
                                 line={"color":"#FF7A00", "width":2},
                                 marker={"color":"#FF7A00", "size":7}))
    fig.update_traces(mode="lines+markers")
    fig.update_xaxes(title="Year")

    
    if version == "v2":
        units_label = const.UNITS_V2["Concentration"][pollutant]
    else:
        units_label = const.UNITS[metric][pollutant]

    
    if pollutant == "PM" and metric == "Concentration":
        y_all = np.concatenate([
            agg["Maximum"].to_numpy(float),
            agg["Mean"].to_numpy(float),
            agg["Minimum"].to_numpy(float),
            city_series[plot_col].to_numpy(float) if not city_series.empty else np.array([])
        ])
        y_top = max(150.0, (np.nanmax(y_all) if y_all.size else 150.0) * 1.10)
        _format_pm25_axis(fig, axis="y", rng=(0, y_top), dtick=50, units_label=units_label)
    else:
        _format_pm25_axis(fig, axis="y", rng=None, units_label=units_label)

    _apply_card_style(fig, legend_bottom=True)
    fig.update_layout(margin=dict(t=44))

    stats = [
        html.Div("Selected City Details:", className="fw-semibold"),
        html.Div(f"City: {city_sel or '—'}"),
        html.Div(f"Country: {country_name or '—'}"),
        html.Div(f"Metric: {metric}"),
    ]
    return fig, stats