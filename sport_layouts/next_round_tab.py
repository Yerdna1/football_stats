from dash import html, dcc, dash_table

from league_names import LEAGUE_NAMES

from .utils import create_league_options
from .styles import table_cell_style, table_header_style, table_style

def create_next_round_tab():
    return dcc.Tab(label='Next Round', children=[
        html.H1("Next Round Fixtures and Analysis",
               style={'text-align': 'center', 'margin': '20px'}),
        
        # League selection
        dcc.Dropdown(
            id='next-round-league-dropdown',
            options=create_league_options(LEAGUE_NAMES),
            value=39,
            style={'width': '80%', 
                   'margin': '0 auto', 
                   'margin-bottom': '20px'}
        ),
        
        # Fixtures section
        html.Div([
            html.H2("Upcoming Fixtures",
                   style={'text-align': 'center', 'margin': '20px'}),
            dash_table.DataTable(
                id='next-fixtures-table',
                columns=[
                    {'name': 'Date', 'id': 'date'},
                    {'name': 'Time', 'id': 'time'},
                    {'name': 'League', 'id': 'league'},
                    {'name': 'Round', 'id': 'round'},
                    {'name': 'Home Team', 'id': 'home_team'},
                    {'name': 'Away Team', 'id': 'away_team'},
                    {'name': 'Venue', 'id': 'venue'},
                    {'name': 'Home', 'id': 'home_odds'},
                    {'name': 'Draw', 'id': 'draw_odds'},
                    {'name': 'Away', 'id': 'away_odds'}
                ],
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': 'rgb(248, 248, 248)'
                    },
                    {
                        'if': {'filter_query': '{is_header} eq true'},
                        'backgroundColor': 'rgb(200, 200, 200)',
                        'fontWeight': 'bold',
                        'fontSize': '16px',
                        'textAlign': 'center'
                    }
                ],
                style_cell={
                    'textAlign': 'left',
                    'padding': '10px',
                    'minWidth': '100px'
                },
                style_header={
                    'backgroundColor': 'rgb(230, 230, 230)',
                    'fontWeight': 'bold'
                }
            )
        ]),
        
        # Team and player statistics
        html.Div([
            html.H2("Match Analysis",
                   style={'text-align': 'center', 'margin': '20px'}),
            
            # Selected match statistics
            dcc.Dropdown(
                id='fixture-select-dropdown',
                placeholder='Select a fixture to analyze',
                style={'width': '50%', 'margin': '20px auto'}
            ),
            
            # Team comparison
            html.Div([
                # Home team stats
                html.Div([
                    html.H3(id='home-team-name', style={'text-align': 'center'}),
                    dash_table.DataTable(
                        id='home-team-stats',
                        style_cell=table_cell_style,
                        style_header=table_header_style,
                        style_table={'width': '80%', 'margin': '10px auto'},
                        style_data={
                            'width': '10%',
                            'maxWidth': '100px',
                            'minWidth': '30px',
                        },
                    )
                ], style={'width': '40%', 'display': 'inline-block'}),
                
                # Away team stats
                html.Div([
                    html.H3(id='away-team-name', style={'text-align': 'center'}),
                    dash_table.DataTable(
                        id='away-team-stats',
                        style_cell=table_cell_style,
                        style_header=table_header_style,
                        style_table={'width': '80%', 'margin': '10px auto'},
                        style_data={
                            'width': '10%',
                            'maxWidth': '100px',
                            'minWidth': '30px',
                        },
                    )
                ], style={'width': '40%', 'display': 'inline-block'})
            ]),
            
            # Key points and analysis
            html.Div([
                html.H3("Match Analysis", style={'text-align': 'center'}),
                html.Div(id='match-analysis',
                        style={'width': '80%', 'margin': '0 auto'})
            ])
        ])
    ])
