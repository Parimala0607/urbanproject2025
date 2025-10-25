# pages/overview.py
from dash import html
import dash_bootstrap_components as dbc
from components.buttons import cta_primary


layout = html.Div([

    
    html.Section([
      
        html.Video(
            id="hero-bg",
            className="hero-video",
            autoPlay=True,
            muted=True,
            loop=True,
            controls=False,
            preload="metadata",
            poster="/assets/overview_hero_poster.jpg",
            children=[
                html.Source(src="/assets/overview.mp4", type="video/mp4"),
                "Your browser does not support the video tag.",
            ],
        ),

        
        html.Div(className="hero-overlay"),

        
        html.Div([
            html.H1(
                ["Urban Air Quality ", html.Span("Explorer")],
                className="hero-title"
            ),
            html.P(
                "Uncover insights into global air pollution and CO₂ emission trends across over 13,000 urban areas from 2000 to 2019. "
                "Empowering data for a healthier planet.",
                className="hero-subtitle"
            ),
            cta_primary(href="/home", id="cta-overview-explore", label="Explore Dashboard"),
        ], className="hero-inner"),

    ], className="hero overview-hero hero--fullscreen"),

    # ===== WHAT WE OFFER =====
    dbc.Card([
        html.Div([
            html.H5("What We Offer", className="section-title"),
            html.Ul([
                html.Li([
                    html.Span("Comprehensive Data", className="bullet-title"),
                    html.Div(
                        "Access and analyze air quality data from 13,000+ cities worldwide spanning two decades (2000–2019) to understand long-term trends.",
                        className="bullet-text"
                    )
                ]),
                html.Li([
                    html.Span("Interactive Visualizations", className="bullet-title"),
                    html.Div(
                        "Use global maps, time-series graphs, and scatter plots to explore patterns and uncover data-driven insights.",
                        className="bullet-text"
                    )
                ]),
                html.Li([
                    html.Span("Downloadable Insights", className="bullet-title"),
                    html.Div(
                        "Download filtered datasets and codebooks for offline analysis, research, or policy development.",
                        className="bullet-text"
                    )
                ]),
            ], className="lead-muted")
        ], className="section-card")
    ], className="card section-card-wrap section-spacer"),

    # ===== IMPACT =====
    dbc.Card([
        html.Div([
            html.H5("Impact", className="section-title"),
            html.Ul([
                html.Li([
                    html.Span("Track Urban Trends", className="bullet-title"),
                    html.Div(
                        "Identify cities with high air pollution and CO₂ emissions, track progress over time, and design targeted interventions for cleaner air and reduced climate impacts.",
                        className="bullet-text"
                    )
                ]),
                html.Li([
                    html.Span("Harmonized Datasets", className="bullet-title"),
                    html.Div(
                        "Access harmonized, city-level datasets to study trends, disparities, and relationships between urbanization, pollution, and health.",
                        className="bullet-text"
                    )
                ]),
                html.Li([
                    html.Span("Interactive Exploration", className="bullet-title"),
                    html.Div(
                        "Explore interactive maps and charts to understand local pollution and climate challenges, and how they compare globally.",
                        className="bullet-text"
                    )
                ]),
                html.Li([
                    html.Span("Evidence-Based Decisions", className="bullet-title"),
                    html.Div(
                        "Support evidence-based decisions with transparent, open, and downloadable data covering two decades (2000–2019) across every urban area in the world.",
                        className="bullet-text"
                    )
                ]),
            ], className="lead-muted")
        ], className="section-card")
    ], className="card section-card-wrap section-spacer"),

    # ===== CHALLENGES =====
    dbc.Card([
        html.Div([
            html.H5("Challenges in Air Quality Data", className="section-title"),
            html.Ul([
                html.Li([
                    html.Span("Data Heterogeneity", className="bullet-title"),
                    html.Div(
                        "Multiple agencies and instruments with inconsistent standards make integration and comparison complex.",
                        className="bullet-text"
                    )
                ]),
                html.Li([
                    html.Span("Missing Information", className="bullet-title"),
                    html.Div(
                        "Many cities or years lack complete records. Historical gaps require imputation and careful interpretation.",
                        className="bullet-text"
                    )
                ]),
            ], className="lead-muted")
        ], className="section-card")
    ], className="card section-card-wrap section-spacer"),

    # ===== MISSION =====
    dbc.Card([
        html.Div([
            html.H5("Our Mission", className="section-title"),
            html.P(
                "We democratize access to critical urban air quality data to foster transparency and enable informed decisions by researchers, policymakers, and communities worldwide.",
                className="lead-muted mb-2"
            ),
            cta_primary(href="/home", id="cta-overview-explore2", label="Explore Now"),
        ], className="section-card text-center")
    ], className="card section-card-wrap section-spacer"),
])
