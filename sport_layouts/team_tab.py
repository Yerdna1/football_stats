from dash import html, dcc, dash_table
from config import LEAGUE_NAMES
from .utils import create_league_options
from .styles import table_cell_style, table_header_style, table_style

def create_team_results_section():
    return html.Div([
        html.H2("Recent Results",
               style={'text-align': 'center', 'margin': '20px 0'}),
        dash_table.DataTable(
            id='team-results-table',
            columns=[
                {'name': 'Date', 'id': 'date'},
                {'name': 'Opponent', 'id': 'opponent'},
                {'name': 'Score', 'id': 'score'},
                {'name': 'Result', 'id': 'result_display'}
            ],
            style_cell={'textAlign': 'center', 'padding': '10px'},
            style_data_conditional=[{
                'if': {'column_id': 'result_display'},
                'fontWeight': 'bold'
            }],
            style_table={'width': '80%', 'margin': '0 auto'}
        )
    ])

def create_scoreless_teams_section():
    return html.Div([
        html.H2("Teams Without Goals",
               style={'text-align': 'center', 'margin': '20px 0'}),
        dash_table.DataTable(
            id='scoreless-teams-table',
            columns=[
                {'name': 'Team', 'id': 'team'},
                {'name': 'Games Without Scoring', 'id': 'scoreless_games'}
            ],
            style_cell={'textAlign': 'center', 'padding': '10px'},
            style_table={'width': '80%', 'margin': '0 auto'}
        )
    ])


def create_team_analysis_tab():
    return dcc.Tab(label='Team Analysis', children=[
        html.H1("Team Analysis",
               style={'text-align': 'center', 'margin': '20px'}),
        
        # League selector
        html.Div([
            html.Label('Select League',
                      style={'display': 'block', 'margin-bottom': '5px', 'text-align': 'center'}),
            dcc.Dropdown(
                id='team-league-dropdown',
                options=create_league_options(LEAGUE_NAMES),
                value=39,
                style={'width': '100%'}
            )
        ], style={'width': '80%', 'margin': '20px auto'}),
        
        # Team selector
        html.Div([
            html.Label('Select Team',
                      style={'display': 'block', 'margin-bottom': '5px', 'text-align': 'center'}),
            dcc.Dropdown(
                id='team-dropdown',
                placeholder='Select a team',
                style={'width': '100%'}
            )
        ], style={'width': '80%', 'margin': '20px auto'}),
        
        dcc.Loading(
            id="team-loading",
            children=[
                html.Div([
                    create_team_results_section(),
                    create_scoreless_teams_section()
                ])
            ]
        )
    ])
