from dash import html, dcc, dash_table

from league_names import LEAGUE_NAMES

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
                            {'name': 'Performance Difference', 'id': 'performance_diff'},
                            {'name': 'Injured Players', 'id': 'injured_players'}
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
                            {
                                'if': {'column_id': 'injured_players'},
                                'color': 'red'
                            }
                        ]
                    )
                ,
                
             # Squad Statistics section
        html.Div([
            html.H2("Squad Statistics Analysis",
                    style={'text-align': 'center', 'margin': '20px 0'}),
            
             # Add team selector
            html.Div([
                html.Label('Select Team',
                          style={'display': 'block', 'margin-bottom': '5px', 'text-align': 'center'}),
                dcc.Dropdown(
                    id='team-selector-dropdown',
                    placeholder='Select a team to view statistics',
                    style={'width': '100%', 'margin-bottom': '20px'}
                )
            ], style={'width': '80%', 'margin': '20px auto'}),
            
            # Stats type selector
            dcc.RadioItems(
                id='stats-type-selector',
                options=[
                    {'label': 'Basic Statistics', 'value': 'basic'},
                    {'label': 'Advanced Statistics', 'value': 'advanced'}
                ],
                value='basic',
                style={'textAlign': 'center', 'margin': '10px 0'},
                inline=True
            ),

            # Basic stats table container
            html.Div(
                id='basic-stats-container',
                children=[
                    dash_table.DataTable(
                        id='player-stats-table',
                        columns=[
                            {'name': 'Player', 'id': 'name'},
                            {'name': 'Position', 'id': 'position'},
                            {'name': 'Age', 'id': 'age'},
                            {'name': 'Apps', 'id': 'appearances'},
                            {'name': 'Minutes', 'id': 'minutes'},
                            {'name': 'Goals', 'id': 'goals'},
                            {'name': 'Assists', 'id': 'assists'},
                            {'name': 'Rating', 'id': 'rating'},
                            {'name': 'Yellow', 'id': 'yellow_cards'},
                            {'name': 'Red', 'id': 'red_cards'}
                        ],
                        data=[],
                        style_data={
                            'whiteSpace': 'normal',
                            'height': 'auto',
                            'textAlign': 'center'
                        },
                        style_cell={
                            'textAlign': 'center',
                            'padding': '10px',
                            'font-family': 'Arial, sans-serif'
                        },
                        style_header={
                            'backgroundColor': 'rgb(230, 230, 230)',
                            'fontWeight': 'bold'
                        },
                        style_table={
                            'overflowX': 'auto',
                            'width': '95%',
                            'margin': '0 auto'
                        },
                        page_size=20,
                        sort_action='native',
                        filter_action='native'
                    )
                ],
                style={'display': 'block'}
            ),

            # Advanced stats table container
            html.Div(
                id='advanced-stats-container',
                children=[
                    dash_table.DataTable(
                        id='advanced-stats-table',
                        columns=[
                            {'name': 'Player', 'id': 'name'},
                            {'name': 'Position', 'id': 'position'},
                            {'name': 'Shots Total', 'id': 'shots_total'},
                            {'name': 'Shots On', 'id': 'shots_on'},
                            {'name': 'Pass %', 'id': 'passes_accuracy'},
                            {'name': 'Key Passes', 'id': 'passes_key'},
                            {'name': 'Tackles', 'id': 'tackles'},
                            {'name': 'Intercept.', 'id': 'interceptions'},
                            {'name': 'Dribbles (S/A)', 'id': 'dribbles_success'},
                            {'name': 'Fouls Drawn', 'id': 'fouls_drawn'}
                        ],
                        data=[],
                        style_data={
                            'whiteSpace': 'normal',
                            'height': 'auto',
                            'textAlign': 'center'
                        },
                        style_cell={
                            'textAlign': 'center',
                            'padding': '10px',
                            'font-family': 'Arial, sans-serif'
                        },
                        style_header={
                            'backgroundColor': 'rgb(230, 230, 230)',
                            'fontWeight': 'bold'
                        },
                        style_table={
                            'overflowX': 'auto',
                            'width': '95%',
                            'margin': '0 auto'
                        },
                        page_size=20,
                        sort_action='native',
                        filter_action='native'
                    )
                ],
                style={'display': 'none'}
            )
        ], style={'margin': '20px 0'})
        ,

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
