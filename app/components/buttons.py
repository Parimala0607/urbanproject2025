# components/buttons.py
import dash_bootstrap_components as dbc
from dash import dcc, html
from pathlib import Path
import pandas as pd

# -----------------------------
# Optional Codebook loader
# -----------------------------
_CODEBOOK_PATH = Path(__file__).resolve().parents[1] / "Data" / "Codebook.csv"
try:
    _df = pd.read_csv(_CODEBOOK_PATH) 
    CODEBOOK_OPTIONS = [
        {"label": r["Column Name"], "value": r["Column Name"]}
        for _, r in _df.iterrows()
    ]
    CODEBOOK_DESC = dict(zip(_df["Column Name"], _df["Description"]))
except Exception:
    CODEBOOK_OPTIONS = []
    CODEBOOK_DESC = {}


def data_version_toggle(id="data-version", value="v1"):
    """Two-button toggle (v1 / v2). IDs produced: f"{id}-v1", f"{id}-v2"."""
    return dbc.ButtonGroup(
        [
            dbc.Button("Version 1", id=f"{id}-v1",
                       color="primary" if value == "v1" else "secondary"),
            dbc.Button("Version 2", id=f"{id}-v2",
                       color="primary" if value == "v2" else "secondary"),
        ],
        className="version-toggle",
    )

def pollutant_type_dropdown(id="pollutant-type"):
    return dcc.Dropdown(
        id=id,
        options=[
            {"label": "PM₂.₅", "value": "PM"},
            {"label": "NO₂",   "value": "NO2"},
            {"label": "O₃",    "value": "O3"},
            {"label": "CO₂",   "value": "CO2"},
        ],
        value="PM",
        clearable=False,
    )

def metric_dropdown(id="metric"):
    return dcc.Dropdown(
        id=id,
        options=[
            {"label": "Concentration", "value": "Concentration"},
            {"label": "PAF",           "value": "PAF"},
            {"label": "Cases",         "value": "Cases"},
            {"label": "Rates",         "value": "Rates"},
        ],
        value="Concentration",
        clearable=False,
    )

def variable_dropdown(id="dd-var", options=None, value=None):
    _opts = options if options is not None else CODEBOOK_OPTIONS
    _val = value if value is not None else (_opts[0]["value"] if _opts else None)
    return dcc.Dropdown(id=id, options=_opts, value=_val, clearable=False,
                        placeholder="Select variable…")

def description_dropdown(id="dd-desc", options=None, value=None):
    return dcc.Dropdown(id=id, options=options or [], value=value,
                        clearable=False, placeholder="Description")

def country_dropdown(id="dd-country", options=None, value=None):
    return dcc.Dropdown(id=id, options=options or [], value=value,
                        clearable=False, placeholder="Country")

def city_dropdown(id="dd-city", options=None, value=None):
    return dcc.Dropdown(id=id, options=options or [], value=value,
                        clearable=False, placeholder="All Cities")

def year_dropdown(id="dd-year", start=2000, end=2020, value=2000):
    """Fixed-range year dropdown."""
    return dcc.Dropdown(
        id=id,
        options=[{"label": str(y), "value": y} for y in range(int(start), int(end) + 1)],
        value=int(value),
        clearable=False,
    )

def download_primary(id="download-filtered", label="Download Filtered Data CSV"):
    return dbc.Button(label, id=id, color="primary", className="px-3")

def cta_primary(id="cta-primary", label="Explore data", href=None):
    return dbc.Button(label, id=id, href=href, color="primary", className="px-3")



def sliders(df):
    """Legacy year slider used by some old pages."""
    yr_min = int(pd.to_numeric(df["Year"], errors="coerce").min())
    yr_max = int(pd.to_numeric(df["Year"], errors="coerce").max())
    marks = {int(y): {"label": str(int(y))}
             for y in sorted(pd.to_numeric(df["Year"], errors="coerce").dropna().unique())}
    return html.Div([
        dcc.Slider(
            id="crossfilter-year--slider",
            min=yr_min, max=yr_max,
            value=2019 if 2019 >= yr_min and 2019 <= yr_max else yr_max,
            marks=marks, step=None, included=False, dots=False,
            tooltip={"placement": "bottom", "always_visible": False},
        )
    ], style={"padding": "0 15px", "marginTop": "15px", "marginBottom": "20px"})

def lin_log(name: str = ""):
    """Legacy X-axis scale control; id='crossfilter-xaxis-type' + name."""
    return html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(
                        html.Span(
                            "X-axis scale:",
                            style={
                                "color": "#000000",
                                "font-size": "16px",
                                "font-family": "helvetica",
                                "padding-right": "5px",
                                "display": "flex",
                                "align-items": "center",
                                "height": "100%",
                                "white-space": "nowrap",
                                "font-weight": "bold",
                            },
                        ),
                        width="auto",
                        style={"padding-right": "5px", "display": "flex", "align-items": "center"},
                    ),
                    dbc.Col(
                        dbc.RadioItems(
                            id="crossfilter-xaxis-type" + name,
                            className="btn-group pollutant-radio-group",
                            inputClassName="btn-check",
                            labelClassName="btn btn-outline-secondary pollutant-button rounded",
                            labelCheckedClassName="btn btn-outline-secondary pollutant-button selected-button rounded",
                            options=[{"label": "Linear", "value": "Linear"},
                                     {"label": "Log", "value": "Log"}],
                            value="Log",
                            labelStyle={"display": "inline-block", "margin": "0", "padding": "0"},
                        ),
                        style={"padding-left": "0px"},
                    ),
                ],
                className="g-0 align-items-center",
            )
        ],
        className="control-group",
        style={"padding": "0px"},
    )

def health_metrics(name: str):
    """Legacy health metrics block; id='health-metrics' + name."""
    tc = dbc.Tooltip(
        "Concentrations for PM2.5, NO2, and O3 are provided as population-weighted average concentrations.",
        target="Concentration", trigger="hover",
    )
    tt = dbc.Tooltip(
        "Population Attributable Fraction (PAF) is the proportion of cases for an outcome that can be attributed to the pollutant among the entire population",
        target="PAF", trigger="hover",
    )
    td = dbc.Tooltip("Annual cases for an outcome attributable to the pollutant", target="Cases", trigger="hover")
    ts = dbc.Tooltip("Annual cases for an outcome attributable to the pollutant per 100K people",
                     target="Rates", trigger="hover")

    return html.Div([
        html.H6("Metric", style={
            "margin-bottom": "5px", "font-weight": "bold", "color": "#000000",
            "font-size": "18px", "font-family": "helvetica"
        }),
        dbc.RadioItems(
            id="health-metrics" + name,
            className="btn-group",
            inputClassName="btn-check",
            labelClassName="btn btn-outline-secondary",
            labelCheckedClassName="selected-button",
            options=[{"label": lab, "value": lab, "label_id": lab}
                     for lab in ["Concentration", "PAF", "Cases", "Rates"]],
            value="Concentration",
            labelStyle={"display": "inline-block"},
        ),
        tc, tt, td, ts
    ], className="control-group")

def details_tip(tar):
    """Legacy tooltip helper used on some pages."""
    return dbc.Tooltip(
        "Click Open Details for more information on the compenents of the webpage.",
        target=tar, trigger="hover focus legacy"
    )

def members():
    """Legacy City Type toggle (C40 vs All Cities)."""
    return html.Div([
        html.H6("City Type", style={
            "margin-bottom": "5px", "font-weight": "bold", "color": "#000000",
            "font-size": "18px", "font-family": "helvetica"
        }),
        html.Div([
            dbc.RadioItems(
                id="c40-toggle",
                className="btn-group pollutant-radio-group",
                inputClassName="btn-check",
                labelClassName="btn btn-outline-secondary pollutant-button",
                labelCheckedClassName="btn btn-outline-secondary pollutant-button selected-button",
                options=[{"label": i, "value": i} for i in ["Members", "All Cities"]],
                value="Members",
                labelStyle={"display": "inline-block", "margin": "0", "padding": "0"},
            )
        ], style={"fontSize": "0", "display": "flex", "whiteSpace": "nowrap"})
    ], className="control-group")

def instruct(ids):
    """Legacy 'Open Details' button with tooltip."""
    return html.Div([
        html.Div(dbc.Button("Open Details", id=ids, n_clicks=0, color="primary"),
                 className="d-grid mx-auto"),
        dbc.Tooltip("Click Open Details for more information on the compenents of the webpage.",
                    id=ids + "tt", target=ids, is_open=True, trigger="hover focus legacy")
    ])

def pol_buttons(ident, selected_value="PM"):
    """Legacy pollutant radio with id='crossfilter-yaxis-column' + ident."""
    props = dict(
        id="crossfilter-yaxis-column" + ident,
        className="btn-group",
        inputClassName="btn-check",
        labelClassName="btn pollutant-button",
        labelCheckedClassName="btn pollutant-button selected-button",
        options=[
            {"label": "PM₂₅", "value": "PM"},
            {"label": "NO₂", "value": "NO2"},
            {"label": "O₃", "value": "O3"},
            {"label": "CO₂", "value": "CO2"},
        ],
        labelStyle={"display": "inline-block"},
    )
    if selected_value is not None:
        props["value"] = selected_value
    return dbc.RadioItems(**props)

def pop_weighted(ident):
    """Legacy data weighting toggle; id='crossfilter-data-type' + ident."""
    return dbc.RadioItems(
        id="crossfilter-data-type" + ident,
        className="btn-group",
        inputClassName="btn-check",
        labelClassName="btn btn-outline-secondary",
        labelCheckedClassName="secondary",
        options=[{"label": i, "value": i} for i in ["Unweighted", "Population Weighted"]],
        value="Unweighted",
        labelStyle={"display": "inline-block"},
    )

def metric_options(is_co2_selected: bool):
    """Legacy metric option builder used by callbacks."""
    if is_co2_selected:
        return [
            {"label": "Concentration", "value": "Concentration"},
            {"label": "PAF", "value": "PAF", "disabled": True},
            {"label": "Cases", "value": "Cases", "disabled": True},
            {"label": "Rates", "value": "Rates", "disabled": True},
        ]
    return [
        {"label": "Concentration", "value": "Concentration"},
        {"label": "PAF", "value": "PAF"},
        {"label": "Cases", "value": "Cases"},
        {"label": "Rates", "value": "Rates"},
    ]

def pol_options(disable_co2: bool):
    """Legacy pollutant options builder."""
    base = [
        {"label": "PM₂₅", "value": "PM"},
        {"label": "NO₂", "value": "NO2"},
        {"label": "O₃", "value": "O3"},
        {"label": "CO₂", "value": "CO2"},
    ]
    if disable_co2:
        base[-1] = {**base[-1], "disabled": True}
    return base

def percent_change_metric():
    """Legacy ‘Percent Change’ selector styled like version buttons."""
    return html.Div([
        html.H6("Metric", style={
            "margin-bottom": "5px", "font-weight": "bold", "color": "#000000",
            "font-size": "18px", "font-family": "helvetica"
        }),
        html.Div([
            html.Div([
                html.Button(
                    "Percent Change in Concentration (2010-2011 vs. 2018-2019)",
                    id="percent-change-button",
                    className="version-button active-version",
                    n_clicks=0
                ),
                dbc.Tooltip(
                    "Percent changes in concentrations of each pollutant from the 2010-2011 2-year average to the 2018-2019 average. 2-year averages were used to reduce the influence of outliers from any single year.",
                    target="percent-change-button", placement="bottom", trigger="hover"
                )
            ], style={"display": "inline-block"})
        ], className="version-button-group")
    ], className="control-group")

def membership():
    """Legacy membership dropdown (labels preserved, including trailing space)."""
    return html.Div([
        html.H6("Membership", style={
            "margin-bottom": "5px", "font-weight": "bold", "color": "#000000",
            "font-size": "18px", "font-family": "helvetica"
        }),
        dcc.Dropdown(
            id="membsDrop",
            options=[
                "All Cities",
                "All Memberships",
                "C40",
                "Global Covenant of Mayors",
                "Breathe Life 2030",
                "Climate Mayors (US ONLY)",
                "Carbon Neutral Cities Alliance ",
                "Resilient Cities Network",
                "Number of Memberships",
            ],
            value="All Cities",
            clearable=False,
            style={"width": "100%", "color": "#123C69", "font-size": "12px", "background-color": "transparent"},
        )
    ], className="year-dropdown", style={"background-color": "transparent"})

def year_dropdown_from_df(df, id="crossfilter-year--slider"):
    """Legacy DF-driven year dropdown."""
    if "Year" not in df.columns:
        years = []
    else:
        years = sorted(pd.to_numeric(df["Year"], errors="coerce").dropna().unique().astype(int))
    latest_year = max(years) if years else None
    default_value = 2019 if 2019 in years else latest_year
    return html.Div([
        html.H6("Year", style={
            "margin-bottom": "5px", "font-weight": "bold", "color": "#000000",
            "font-size": "18px", "font-family": "helvetica"
        }),
        dcc.Dropdown(
            id=id,
            options=[{"label": str(y), "value": int(y)} for y in years],
            value=default_value,
            clearable=False,
            style={"width": "100%", "color": "#123C69", "font-size": "12px", "background-color": "transparent"},
        )
    ], className="year-dropdown", style={"background-color": "transparent"})


def year_dropdown_df(df):
    return year_dropdown_from_df(df)


year_dropdown_legacy = year_dropdown_from_df
