import dash_bootstrap_components as dbc
from dash import dcc, html

# 1. Data Version Toggle (ButtonGroup)

def data_version_toggle(id="data-version", value="v1"):
    return dbc.ButtonGroup([
        dbc.Button("Version 1", id=f"{id}-v1",
                   color="primary" if value=="v1" else "secondary"),
        dbc.Button("Version 2", id=f"{id}-v2",
                   color="primary" if value=="v2" else "secondary"),
    ], className="version-toggle")

# 2. Pollutant Type Dropdown
def pollutant_type_dropdown(id="pollutant-type"):
    return dcc.Dropdown(
        id=id,
        options=[
            {"label": "PM₂.₅", "value": "pm25"},
            {"label": "NO₂", "value": "no2"},
            {"label": "O₃", "value": "o3"},
            {"label": "CO₂", "value": "co2"},
        ],
        value="pm25",
        clearable=False
    )

# 3. Metric Dropdown
def metric_dropdown(id="metric"):
    return dcc.Dropdown(
        id=id,
        options=[
            {"label": "Concentration", "value": "concentration"},
            {"label": "PAF", "value": "paf"},
            {"label": "Cases", "value": "cases"},
            {"label": "Rate", "value": "rate"},
        ],
        value="concentration",
        clearable=False
    )

def primary_button(id="primary-btn", label="Submit"):
    return dbc.Button(label, id=id, color="primary", className="me-2")

def success_button(id="success-btn", label="Success"):
    return dbc.Button(label, id=id, color="success", className="me-2")

def danger_button(id="danger-btn", label="Reset"):
    return dbc.Button(label, id=id, color="danger", className="me-2")

def secondary_button(id="secondary-btn", label="Back", href="/"):
    return dbc.Button(label, id=id, color="secondary", className="me-2", href=href)
