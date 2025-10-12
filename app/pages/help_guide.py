from dash import html
import dash_bootstrap_components as dbc

from components.card import card

questions = [
    "How to Use the Global Map?",
    "Filtering and Downloading Data.",
    "Understandind Percentage Change.",
    "Country vs City-Level Data View.",
    "Using the Network and Stage Pages."
]
# layout = dbc.Container([
#         html.H2("Help & Guide", className="m-3") ] + 
#        [card(text=value, icon="+", idx=i) for i, value in enumerate(questions)  
# ],
# )

layout = dbc.Container(
    [html.H2("Help & Guide", className="m-3")]
    + [card(text=value, icon="+", idx=i) for i, value in enumerate(questions)], 
    fluid=True,
)