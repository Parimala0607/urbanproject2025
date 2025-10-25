# pages/home.py
from dash import ctx, dcc, html, callback, Input, Output, State, dash_table
from dash.dependencies import ALL
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import math
from dash.exceptions import PreventUpdate

from components.buttons import CODEBOOK_DESC
from components import data_prep

df = data_prep.DFILT
PAGE_SIZE = 8  


try:
    from components.maps import worldmap2_atlas_like
    _MAP_OK = True
    _MAP_ERR = None
except Exception as _e:
    worldmap2_atlas_like = None
    _MAP_OK = False
    _MAP_ERR = _e

from components.buttons import (
    data_version_toggle,
    pollutant_type_dropdown,
    metric_dropdown,
    variable_dropdown,
    description_dropdown,
    country_dropdown,
    city_dropdown,
    year_dropdown,
    download_primary,
)



def _placeholder_df() -> pd.DataFrame:
    return pd.DataFrame([
        {"iso3": "USA", "value": 45}, {"iso3": "CAN", "value": 60},
        {"iso3": "MEX", "value": 30}, {"iso3": "BRA", "value": 35},
        {"iso3": "GBR", "value": 65}, {"iso3": "FRA", "value": 62},
        {"iso3": "DEU", "value": 63}, {"iso3": "ESP", "value": 58},
        {"iso3": "NGA", "value": 20}, {"iso3": "EGY", "value": 40},
        {"iso3": "ZAF", "value": 38}, {"iso3": "IND", "value": 25},
        {"iso3": "CHN", "value": 50}, {"iso3": "AUS", "value": 70},
    ])

def _fallback_worldmap(df_in: pd.DataFrame, title: str = ""):
    fig = px.choropleth(
        df_in, locations="iso3", color="value",
        color_continuous_scale="Magma", projection="natural earth", title=title,
    )
    fig.update_layout(margin=dict(l=0, r=0, t=40, b=0))
    return fig

def _apply_filters(_df, var_value, desc_value, country_value, city_value, y_from, y_to):
    out = _df.copy()
    if var_value:
        for cand in ["Variable", "Variable Name", "VARIABLE", "VarName"]:
            if cand in out.columns:
                out = out[out[cand] == var_value]
                break
    if desc_value:
        for cand in ["Description", "DESCRIPTION", "Desc"]:
            if cand in out.columns:
                out = out[out[cand] == desc_value]
                break
    if country_value and "Country" in out.columns:
        out = out[out["Country"] == country_value]
    if city_value:
        if "CityCountry" in out.columns:
            out = out[out["CityCountry"] == city_value]
        elif "City" in out.columns:
            out = out[out["City"] == city_value]
    year_col = next((c for c in ["Year", "year", "YEAR"] if c in out.columns), None)
    if year_col:
        if y_from is not None:
            out = out[out[year_col] >= int(y_from)]
        if y_to is not None:
            out = out[out[year_col] <= int(y_to)]
    return out

def _build_pager(current, total_pages):
    btns = []
    btns.append(
        dbc.Button("Previous", id={"type": "dd-page-btn", "page": "prev"},
                   color="secondary", outline=True, size="sm",
                   disabled=(current <= 0), className="me-2")
    )
    for i in range(total_pages):
        btns.append(
            dbc.Button(str(i + 1),
                       id={"type": "dd-page-btn", "page": i},
                       color=("primary" if i == current else "light"),
                       size="sm",
                       className=("me-2" if i < total_pages - 1 else ""))
        )
    btns.append(
        dbc.Button("Next", id={"type": "dd-page-btn", "page": "next"},
                   color="secondary", outline=True, size="sm",
                   disabled=(current >= total_pages - 1), className="ms-1")
    )
    return html.Div(btns)

# ------------------------
# Sections
# ------------------------

def map_section():
    df_local = _placeholder_df()
    try:
        if _MAP_OK and callable(worldmap2_atlas_like):
            fig = worldmap2_atlas_like(
                df_country=df_local,
                title="WORLD ATLAS 2.0",
                subtitle="Demo map (swap with real data later)",
                location_col="iso3", value_col="value", use_iso3=True,
                labels_df=None, color_scale="Magma", value_units="",
                cmin=None, cmax=None,
            )
        else:
            fig = _fallback_worldmap(df_local)
    except Exception:
        fig = _fallback_worldmap(df_local)

    return html.Div([
        html.H3("Global Pollution Map", className="mb-3"),
        dbc.Card([
            dbc.CardHeader("Common Filters", className="fw-semibold"),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col(html.Div([
                        html.Label("Data Version", className="form-label fw-semibold mb-1"),
                        data_version_toggle(id="data-version", value="v1"),
                    ]), md=4),
                    dbc.Col(html.Div([
                        html.Label("Pollutant Type", className="form-label fw-semibold mb-1"),
                        pollutant_type_dropdown(id="pollutant-type"),
                    ]), md=4),
                    dbc.Col(html.Div([
                        html.Label("Metric", className="form-label fw-semibold mb-1"),
                        metric_dropdown(id="metric"),
                    ]), md=4),
                ], className="g-2"),
            ]),
        ], className="mb-3"),
        dbc.Card([
            dbc.CardBody([
                dcc.Graph(id="worldmap-graph", style={"height": "68vh"}, figure=fig),
                dbc.Alert(
                    f"Fallback map renderer loaded{f' due to: {_MAP_ERR}' if not _MAP_OK else ''}",
                    color="warning", className="mt-2",
                    style={"display": "none" if _MAP_OK else "block"},
                ),
            ])
        ], className="mb-3"),
    ])

def change_section():
    return html.Div([
        html.H3("Percent Change Visualization (2000 vs 2019)", className="mb-3"),
        dbc.Card([
            dbc.CardHeader("Common Filters", className="fw-semibold"),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col(html.Div([
                        html.Label("Data Version", className="form-label fw-semibold mb-1"),
                        data_version_toggle(id="pc-data-version", value="v1"),
                    ]), md=4),
                    dbc.Col(html.Div([
                        html.Label("Pollutant Type", className="form-label fw-semibold mb-1"),
                        pollutant_type_dropdown(id="pc-pollutant"),
                    ]), md=4),
                    dbc.Col(html.Div([
                        html.Label("Metric", className="form-label fw-semibold mb-1"),
                        metric_dropdown(id="metric"),
                    ]), md=4),
                ], className="g-2"),
            ]),
        ], className="mb-3"),
        dbc.Card([
            dbc.CardBody(
                html.Div(
                    "Percent Change map will go here...",
                    className="text-muted",
                    style={
                        "height": "420px", "display": "flex",
                        "alignItems": "center", "justifyContent": "center",
                        "border": "1px dashed #ced4da", "borderRadius": "6px",
                    },
                )
            )
        ]),
    ])

def about_section():
    return html.Div([
        html.H2("About Urban Air Quality Explorer", className="mb-3 fw-bold"),
        dbc.Card([
            dbc.CardBody([
                html.H5("More Information", className="fw-semibold"),
                html.P(
                    "The Urban Air Quality Explorer is a comprehensive web dashboard designed to visualize "
                    "and analyze air pollution levels across 13,189 urban areas worldwide from 2000 to 2019. "
                    "Our mission is to provide accessible insights into global air quality trends, supporting "
                    "researchers, policymakers, and the public in understanding the impact of urban pollution.",
                ),
                html.P(
                    "This platform offers interactive maps, percentage change visualizations, and detailed data "
                    "tables, allowing users to explore pollutant types (PM₂.₅, NO₂, O₃, CO₂), various metrics "
                    "(Concentration, PAF, Cases, Rate), and temporal trends. We aim to foster informed "
                    "decision-making for a healthier urban environment.",
                ),
                html.H5("Acknowledgements", className="mt-4 fw-semibold"),
                html.P(
                    "We extend our sincere gratitude to the various organizations and individuals whose invaluable "
                    "contributions made this project possible. Special thanks to the data providers for their "
                    "commitment to open access environmental data, which forms the backbone of this explorer.",
                ),
                html.H5("Contact", className="mt-4 fw-semibold"),
                html.P("For inquiries, feedback, or collaboration opportunities, please feel free to reach out:"),
                html.Ul([
                    html.Li("Email: sooyeonkim@gwu.edu"),
                    html.Li("Email: sanenberg@email.gwu.edu"),
                ]),
                html.Hr(className="my-4"),
                html.Div("© 2025 Urban Air Quality Explorer. All rights reserved.", className="text-muted"),
            ])
        ]),
    ])

def data_download_section():
    return html.Div([
        html.H3("Data & Download", className="mb-3"),

        dbc.Card([
            dbc.CardHeader("Filter Data", className="fw-semibold"),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([html.Label("Variable Name", className="form-label fw-semibold mb-1"),
                             variable_dropdown(id="dd-var")], md=3),
                    dbc.Col([html.Label("Description", className="form-label fw-semibold mb-1"),
                             description_dropdown(id="dd-desc")], md=3),
                    dbc.Col([html.Label("Country", className="form-label fw-semibold mb-1"),
                             country_dropdown(id="dd-country", options=[], value=None)], md=3),
                    dbc.Col([html.Label("City", className="form-label fw-semibold mb-1"),
                             city_dropdown(id="dd-city", options=[], value=None)], md=3),
                ], className="g-3"),

                dbc.Row([
                    dbc.Col([html.Label("Year From", className="form-label fw-semibold mb-1"),
                             year_dropdown(id="dd-year-from", start=2000, end=2020, value=2000)], md=3),
                    dbc.Col([html.Label("Year To", className="form-label fw-semibold mb-1"),
                             year_dropdown(id="dd-year-to", start=2000, end=2020, value=2020)], md=3),
                    dbc.Col(), dbc.Col(),
                ], className="g-3 mt-1"),

                dbc.Row(
                    dbc.Col(
                        html.Div([
                            dbc.Button(
                                "Download Full CSV",
                                href="https://raw.githubusercontent.com/anenbergresearch/app-files/main/unified_data_SYK_Apr2025.csv",
                                download="unified_data.csv",
                                id="download-full",
                                external_link=True,
                                color="primary",
                                className="px-3"
                            ),
                            download_primary(id="dd-download", label="Download Filtered Data CSV"),
                            dcc.Download(id="dd-download-file"),
                        ],
                        className="d-flex justify-content-end gap-3 mt-3"),
                        width=12
                    )
                ),
            ]),
        ], className="mb-3"),

        dbc.Card([
            dbc.CardHeader("Data", className="fw-semibold"),
            dbc.CardBody([
                dash_table.DataTable(
                    id="dd-table",
                    columns=[{"name": c, "id": c} for c in df.columns],
                    data=[],
                    page_action="none",           
                    fixed_rows={"headers": True},
                    style_table={
                        "height": "420px",
                        "overflowY": "auto",
                        "overflowX": "auto",
                        "borderRadius": "10px",
                        "border": "1px solid #e9ecef",
                    },
                    style_as_list_view=True,
                    style_header={
                        "backgroundColor": "#f8f9fb",
                        "fontWeight": "600",
                        "borderBottom": "1px solid #e9ecef",
                        "position": "sticky",
                        "top": 0,
                        "zIndex": 1,
                    },
                    style_cell={
                        "textAlign": "left", "padding": "12px", "fontSize": 15,
                        "minWidth": 80, "width": 120, "maxWidth": 340,
                    },
                    style_data={"borderBottom": "1px solid #f1f3f5"},
                    style_data_conditional=[{"if": {"row_index": "odd"}, "backgroundColor": "#fcfdff"}],
                    css=[
                        {"selector": ".dash-spreadsheet-container .dash-spreadsheet-inner tr:hover td",
                         "rule": "background-color: #f8fafc;"},
                        {"selector": ".dash-table-container .dash-table-pagination",
                         "rule": "display: none;"},
                    ],
                ),
                html.Div(id="dd-pager", className="d-flex justify-content-center mt-3"),
                html.Div(id="dd-summary", className="text-muted text-center mt-1", style={"fontSize": "12px"}),
                dcc.Store(id="dd-page", data=0),
                dcc.Store(id="dd-total-pages", data=1),
            ]),
        ]),
    ])

def blank_placeholder(text):
    return dbc.Alert(text, color="secondary", className="mb-0")

# ------------------------
# Page Layout 
# ------------------------

layout = html.Div([html.Div(id="home-content")], className="p-0")

@callback(Output("home-content", "children"), Input("url", "pathname"))
def render_home_section(pathname: str):
    if not pathname or not pathname.startswith("/home"):
        raise PreventUpdate
    if pathname in ("/home", "/home/map"):
        return map_section()
    if pathname == "/home/change":
        return change_section()
    if pathname == "/home/data":
        return data_download_section()
    if pathname == "/home/about":
        return about_section()
    return blank_placeholder("Unknown Home section.")

# ------------------------
# Data & Download callbacks
# ------------------------

@callback(
    Output("dd-desc", "options"),
    Output("dd-desc", "value"),
    Input("dd-var", "value"),
)
def _sync_desc(var_value):
    if not var_value:
        return [], None
    desc = CODEBOOK_DESC.get(var_value, "")
    opts = [{"label": desc, "value": desc}] if desc else []
    return opts, (desc or None)

@callback(
    Output("dd-country", "options"),
    Output("dd-country", "value"),
    Input("dd-country", "id"),
    prevent_initial_call=False
)
def load_countries(_):
    if "Country" not in df.columns:
        return [], None
    opts = [{"label": c, "value": c} for c in sorted(df["Country"].dropna().unique())]
    return opts, (opts[0]["value"] if opts else None)

@callback(
    Output("dd-city", "options"),
    Output("dd-city", "value"),
    Input("dd-country", "value"),
)
def load_cities(selected_country):
    if not selected_country:
        return [], None
    filtered = df[df["Country"] == selected_country]
    city_col = "CityCountry" if "CityCountry" in df.columns else "City"
    opts = [{"label": c, "value": c} for c in sorted(filtered[city_col].dropna().unique())]
    return opts, (opts[0]["value"] if opts else None)

@callback(
    Output("dd-year-to", "value"),
    Input("dd-year-from", "value"),
    State("dd-year-to", "value"),
    prevent_initial_call=False
)
def _keep_year_bounds(y_from, y_to):
    if y_from is None or y_to is None:
        return y_to
    return max(int(y_from), int(y_to))


@callback(
    Output("dd-table", "data"),
    Output("dd-table", "columns"),
    Output("dd-summary", "children"),
    Output("dd-pager", "children"),
    Output("dd-total-pages", "data"),
    Input("dd-var", "value"),
    Input("dd-desc", "value"),
    Input("dd-country", "value"),
    Input("dd-city", "value"),
    Input("dd-year-from", "value"),
    Input("dd-year-to", "value"),
    Input("dd-page", "data"),  
)
def _refresh_table(var_value, desc_value, country_value, city_value, y_from, y_to, page_current):
    filtered = _apply_filters(df, var_value, desc_value, country_value, city_value, y_from, y_to)
    total_rows = len(filtered)
    total_pages = max(1, math.ceil(total_rows / PAGE_SIZE))
    cur = max(0, min(int(page_current or 0), total_pages - 1))
    start, end = cur * PAGE_SIZE, min((cur + 1) * PAGE_SIZE, total_rows)
    page_df = filtered.iloc[start:end] if total_rows else filtered.head(0)
    cols = [{"name": c, "id": c} for c in page_df.columns]
    summary = f"Showing {start + 1 if total_rows else 0} - {end if total_rows else 0} of {total_rows} entries."
    pager = _build_pager(cur, total_pages)
    return page_df.to_dict("records"), cols, summary, pager, total_pages

@callback(
    Output("dd-page", "data"),
    Input({"type": "dd-page-btn", "page": ALL}, "n_clicks"),
    State("dd-page", "data"),
    State("dd-total-pages", "data"),
    prevent_initial_call=True
)
def _on_pager_click(n_clicks_list, current_page, total_pages):
    if not n_clicks_list or all((x or 0) == 0 for x in n_clicks_list):
        raise PreventUpdate
    trig = ctx.triggered_id
    if not trig or "page" not in trig:
        raise PreventUpdate
    cur = int(current_page or 0)
    max_page = max(0, int((total_pages or 1) - 1))
    p = trig["page"]
    if p == "prev":
        return max(0, cur - 1)
    if p == "next":
        return min(max_page, cur + 1)
    try:
        num = int(p)
    except Exception:
        raise PreventUpdate
    return max(0, min(num, max_page))

@callback(
    Output("dd-download-file", "data"),
    Input("dd-download", "n_clicks"),
    State("dd-var", "value"),
    State("dd-desc", "value"),
    State("dd-country", "value"),
    State("dd-city", "value"),
    State("dd-year-from", "value"),
    State("dd-year-to", "value"),
    prevent_initial_call=True
)
def _download_filtered(n, var_value, desc_value, country_value, city_value, y_from, y_to):
    if not n:
        raise PreventUpdate
    filtered = _apply_filters(df, var_value, desc_value, country_value, city_value, y_from, y_to)
    return dcc.send_data_frame(filtered.to_csv, "uaqe_filtered.csv", index=False)
