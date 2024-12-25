from dash import html, dcc, dash_table
from config import LEAGUE_NAMES
from .utils import create_league_options
from .styles import table_cell_style, table_header_style, table_style

def preprocess_form_data(data):
    """
    Preprocesses the 'form' column into a list of HTML spans for conditional formatting.
    """
    for row in data:
        form = row.get("form", "")
        styled_form = ""
        for char in form:
            if char == "W":
                styled_form += f"<span style='background-color: green; color: white; padding: 2px 4px; margin: 1px; border-radius: 3px;'>{char}</span>"
            elif char == "L":
                styled_form += f"<span style='background-color: red; color: white; padding: 2px 4px; margin: 1px; border-radius: 3px;'>{char}</span>"
            else:
                styled_form += f"<span style='margin: 1px;'>{char}</span>"
        row["form"] = styled_form
    return data

def create_form_analysis_tab():
    return dcc.Tab(label='Form Analysis', children=[
        html.H1("Team Form Analysis",
                style={'text-align': 'center', 'margin': '20px'}),

        # League selector
        html.Div([
            html.Label('Select League',
                       style={'display': 'block', 'margin-bottom': '5px', 'text-align': 'center'}),
            dcc.Dropdown(
                id='form-league-dropdown',
                options=create_league_options(LEAGUE_NAMES),
                value=39,
                style={'width': '100%'}
            )
        ], style={'width': '80%', 'margin': '20px auto'}),

        # Form length selector
        html.Div([
            html.Label('Form Analysis Length',
                       style={'display': 'block', 'margin-bottom': '5px', 'text-align': 'center'}),
            dcc.RadioItems(
                id='form-length-selector',
                options=[
                    {'label': 'Last 3 matches', 'value': 3},
                    {'label': 'Last 5 matches', 'value': 5}
                ],
                value=3,
                style={'textAlign': 'center', 'margin': '10px 0'},
                inline=True
            )
        ], style={'width': '80%', 'margin': '20px auto'}),

        # Tables section
        dcc.Loading(
            id="form-loading",
            children=[
                # Form Analysis Table
                html.Div([
                    html.H2("Form vs Actual Performance Analysis",
                            style={'text-align': 'center', 'margin': '20px 0'}),
                    dash_table.DataTable(
                        id='form-analysis-table',
                        columns=[
                            {'name': 'Team', 'id': 'team'},
                            {'name': 'League', 'id': 'league'},
                            {'name': 'Current Position', 'id': 'current_position'},
                            {'name': 'Points', 'id': 'current_points'},
                            {'name': 'PPG', 'id': 'current_ppg'},
                            {'name': 'Recent Form', 'id': 'form', 'presentation': 'markdown'},
                            {'name': 'Form Points', 'id': 'form_points'},
                            {'name': 'Form PPG', 'id': 'form_ppg'},
                            {'name': 'Performance Difference', 'id': 'performance_diff'}
                        ],
                        style_cell=table_cell_style,
                        style_header=table_header_style,
                        style_table=table_style,
                        data=[],
                        # Allow HTML content
                        style_data_conditional=[
                            {
                                'if': {'column_id': 'performance_diff', 'filter_query': '{performance_diff} > 0'},
                                'color': 'green',
                                'fontWeight': 'bold'
                            },
                            {
                                'if': {'column_id': 'performance_diff', 'filter_query': '{performance_diff} < 0'},
                                'color': 'red',
                                'fontWeight': 'bold'
                            },
                        ]
                    )
                ]),

                # Upcoming Fixtures Table
                html.Div([
                    html.H2("Upcoming Fixtures for Top Form-Changing Teams",
                            style={'text-align': 'center', 'margin': '30px 0 20px 0'}),
                    dash_table.DataTable(
                        id='upcoming-fixtures-table',
                        columns=[
                            {'name': 'Team', 'id': 'team'},
                            {'name': 'Performance Diff', 'id': 'performance_diff'},
                            {'name': 'Next Opponent', 'id': 'next_opponent'},
                            {'name': 'Date', 'id': 'date'},
                            {'name': 'Time', 'id': 'time'},
                            {'name': 'Venue', 'id': 'venue'}
                        ],
                        style_cell=table_cell_style,
                        style_header=table_header_style,
                        style_table=table_style,
                        
                        data=[],
                             style_data_conditional=[
                            {
                                'if': {'column_id': 'performance_diff', 'filter_query': '{performance_diff} > 0'},
                                'color': 'green',
                                'fontWeight': 'bold'
                            },
                            {
                                'if': {'column_id': 'performance_diff', 'filter_query': '{performance_diff} < 0'},
                                'color': 'red',
                                'fontWeight': 'bold'
                            },
                        ]
                    )
                ])
            ]
        )
    ])
