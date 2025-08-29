from dash import html
import dash_bootstrap_components as dbc

navbar = dbc.Navbar(
    dbc.Container([
        # App title
        html.A(
            dbc.Row([
                dbc.Col(html.Span("Urban Air Quality Explorer",
                                  className="navbar-brand mb-0 h1 text-white")),
            ], align="center"),
            href="/overview", style={"textDecoration": "none"}
        ),

        # Nav links
        dbc.Nav([
            dbc.NavItem(dbc.NavLink("Overview",  href="/overview",  id="link-overview",  className="text-white")),
            dbc.NavItem(dbc.NavLink("Home",      href="/home",      id="link-home",      className="text-white")),
            dbc.NavItem(dbc.NavLink("Networks",  href="/networks",  id="link-networks",  className="text-white")),
            dbc.NavItem(dbc.NavLink("Countries", href="/countries", id="link-countries", className="text-white")),
            dbc.NavItem(dbc.NavLink("States",    href="/states",    id="link-states",    className="text-white")),
            dbc.NavItem(dbc.NavLink("Help & Guide", href="/help_guide", id="link-help", className="text-white")),
        ], className="me-auto flex-grow-1 justify-content-end"),

        
        dbc.Row([
            dbc.Col(html.Img(src="/assets/Milken_Institute_School_of_Public_Health.jpg", height="40px"), className="me-2"),
            dbc.Col(html.Img(src="/assets/HAQAST.png", height="40px"), className="me-2"),
            dbc.Col(html.Img(src="/assets/REACH.jpg", height="40px")),
        ], className="ms-auto")   
    ]),
    color="primary",
    dark=True,
    sticky="top",
)
