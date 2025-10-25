# from dash import html
# import dash_bootstrap_components as dbc

# def card(text, icon, idx):
#     return dbc.CardBody([
#         dbc.Row([
#                 # dbc.Col(
#                 #     html.Div(html.P(text, className="text-muted")),
#                 #     width="auto"
#                 # ),
#                 # dbc.Col(
#                 #     html.Span(icon, style={
#                 #             "float": "right",
#                 #             "fontWeight": "bold",
#                 #             "fontSize": "20px",
#                 #             "cursor": "pointer"} # Note: Move this to common sheet
#                 #             )
#                 # ),
#                         dbc.Col(
#                         html.P(text, className="text-muted mb-0"),
#                         width="auto"
#                         ),
#                         dbc.Col(
#                             html.Span(
#                                 icon,
#                                 id=f"toggle-icon-{idx}",
#                                 style={
#                                     "float": "right",
#                                     "fontWeight": "bold",
#                                     "fontSize": "20px",
#                                     "cursor": "pointer"
#                                 }
#                             )
#                         ),

#             ],
#             align="top"
#         )],
#         className="shadow-sm m-3 px-2 py-2 bg-light border border-shadow rounded"
#         )

from dash import html
import dash_bootstrap_components as dbc

def card(text, icon, idx):
    """
    Create a single card with collapsible content.
    """
    return dbc.CardBody(
        [
            dbc.Row(
                [
                    dbc.Col(
                        html.P(text, className="text-muted fs-6"),
                        width="auto",
                    ),
                    dbc.Col(
                        html.Span(
                            icon,
                            id=f"toggle-icon-{idx}",  
                            # -- Have to add this in  Style sheet
                            style={
                                "fontWeight": "bold",
                                "fontSize": "20px",
                                "cursor": "pointer"
                            },
                        ),
                            className="d-flex align-items-center justify-content-end"
                    ),
                ],
                align="baseline",
            ),
            dbc.Collapse(
                dbc.CardBody(
                     html.P("Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum", className="text-muted fs-6"),
                ),
                id=f"collapse-{idx}",
                is_open=False,
            ),
        ],
        className="shadow-sm m-3 px-2 py-2 ps-3 pe-4 bg-light border rounded",
    )

