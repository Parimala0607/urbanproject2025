# components/maps.py
import plotly.express as px
import plotly.graph_objects as go

def worldmap2_atlas_like(
    df_country,
    *,
    title="WORLD ATLAS 2.0",
    subtitle="",
    location_col="iso3",    
    value_col="value",
    use_iso3=True,
    labels_df=None,           
    color_scale="Magma",      
    value_units="",
    cmin=None, cmax=None
):
    kw = dict(locations=location_col)
    if use_iso3:
        kw["locationmode"] = "ISO-3"

    fig = px.choropleth(
        df_country,
        **kw,
        color=value_col,
        projection="natural earth",
        color_continuous_scale=f"{color_scale}_r",
        range_color=None if (cmin is None or cmax is None) else (cmin, cmax),
    )

    fig.update_geos(
        showcountries=True,  countrycolor="rgba(70,70,70,0.55)",
        showcoastlines=True, coastlinecolor="rgba(70,70,70,0.55)",
        showland=True,  landcolor="#e1e7ee",
        showocean=True, oceancolor="#ecf1f6",
        showlakes=True, lakecolor="#ecf1f6",
        fitbounds="locations",
        bgcolor="white",
    )
    fig.update_traces(
        marker_line_width=0.75,
        marker_line_color="rgba(60,60,60,0.55)",
        hovertemplate="<b>%{location}</b><br>%{z:.2f}<extra></extra>"
                      if not value_units else
                      f"<b>%{{location}}</b><br>{value_units}: %{{z:.2f}}<extra></extra>"
    )
    fig.update_coloraxes(
        colorbar_title=value_units,
        ticks="outside", ticklen=6, thickness=18,
        lenmode="pixels", len=380, outlinewidth=0.6,
        tickfont=dict(size=10, color="#333"),
    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="white", plot_bgcolor="white",
        annotations=[
            dict(text=title, x=0.5, y=1.05, xref="paper", yref="paper",
                 showarrow=False, font=dict(size=36, color="white", family="Arial Black"),
                 align="center", bgcolor="rgba(60,60,60,0.65)", borderpad=10),
            dict(text=subtitle, x=0.5, y=1.002, xref="paper", yref="paper",
                 showarrow=False, font=dict(size=14, color="white"),
                 align="center", bgcolor="rgba(60,60,60,0.50)", borderpad=6),
            dict(text="<b>HIGH</b>", x=1.02, y=0.98, xref="paper", yref="paper",
                 showarrow=False, font=dict(size=11, color="#111")),
            dict(text="<b>LOW</b>",  x=1.02, y=0.02, xref="paper", yref="paper",
                 showarrow=False, font=dict(size=11, color="#111")),
        ],
    )

    if labels_df is not None and len(labels_df) > 0:
        fig.add_trace(go.Scattergeo(
            lon=labels_df["lon"], lat=labels_df["lat"],
            text=labels_df["label"], mode="text",
            textfont=dict(size=9, color="rgba(60,60,60,0.65)"),
            hoverinfo="skip", showlegend=False,
        ))
    return fig
