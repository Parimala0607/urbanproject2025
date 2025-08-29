from dash import html
import dash_bootstrap_components as dbc

def nav_item(href, label, icon):
    """Helper to render a link with an icon."""
    return dbc.NavLink(
        [
            html.I(className=f"bi {icon} me-2"),
            html.Span(label),
        ],
        href=href,
        active="exact",            
        className="side-link nav-link",
        id=f"side-{label.lower().replace(' & ', '-').replace(' ', '-')}"
    )

sidebar = html.Div(
    dbc.Card(
        [
            html.Div("Home Sections", className="sidebar-title px-3 pt-3 pb-2"),
            dbc.Nav(
                [
                    nav_item("/home/map",    "Map",             "bi-geo-alt"),
                    nav_item("/home/change", "Percent Change",  "bi-sliders"),
                    nav_item("/home/data",   "Data & Download", "bi-download"),
                    nav_item("/home/about",  "About",           "bi-info-circle"),
                ],
                vertical=True,
                className="sidebar-nav px-3 pb-3"
            ),
        ],
        className="sidebar-panel shadow-sm"
    )
)
