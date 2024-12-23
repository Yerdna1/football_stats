from dash import html, dcc, dash_table
from config import LEAGUE_NAMES

def create_winless_streaks_tab():
    return dcc.Tab(label='Winless Streaks', children=[
        html.H1("Winless Streaks in Top 5 European Leagues", 
               style={'text-align': 'center', 
                     'margin-bottom': '30px',
                     'margin-top': '20px',
                     'font-family': 'Arial, sans-serif'}),
        dcc.Dropdown(
            id='league-dropdown',
            options=[{'label': name, 'value': id_} 
                    for id_, name in LEAGUE_NAMES.items()],
            value=39,
            style={'width': '50%', 
                   'margin': '0 auto', 
                   'margin-bottom': '20px'}
        ),
        html.Div([
            dcc.Checklist(
                id='current-streak-filter',
                options=[{'label': 'Show Only Current Running Streaks', 
                         'value': 'current'}],
                value=[],
                style={'textAlign': 'center', 'margin': '10px 0'}
            )
        ]),
        dcc.Loading(
            id="loading",
            children=[
                dcc.Graph(id='winless-streaks-chart'),
                create_last_matches_table()
            ],
            type="circle"
        )
    ])

def create_team_analysis_tab():
    return dcc.Tab(label='Team Analysis', children=[
        html.H1("Team Analysis",
               style={'text-align': 'center', 'margin': '20px'}),
        create_team_selection(),
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

def create_last_matches_table():
    return html.Div([
        html.H2("Last Results for Top 5 Winless Teams",
               style={'text-align': 'center',
                     'margin': '20px 0',
                     'font-family': 'Arial, sans-serif'}),
        dash_table.DataTable(
            id='last-matches-table',
            columns=[
                {'name': 'Team', 'id': 'team'},
                {'name': 'Winless Streak', 'id': 'streak'},
                {'name': 'Last Match Result', 'id': 'result'},
                {'name': 'Score', 'id': 'score'},
                {'name': 'Date', 'id': 'date'}
            ],
            style_cell=table_cell_style,
            style_header=table_header_style,
            style_table=table_style,
            style_data_conditional=table_conditional_style
        )
    ])

def create_team_selection():
    return html.Div([
        html.Div([
            html.Label('Select League'),
            dcc.Dropdown(
                id='team-league-dropdown',
                options=[{'label': name, 'value': id_} 
                       for id_, name in LEAGUE_NAMES.items()],
                value=39
            ),
        ], style={'width': '30%', 'margin': '10px auto'}),
        html.Div([
            html.Label('Select Team'),
            dcc.Dropdown(
                id='team-dropdown',
                placeholder='Select a team'
            ),
        ], style={'width': '30%', 'margin': '10px auto'})
    ])

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

# Table styles
table_cell_style = {
    'textAlign': 'left',
    'padding': '10px',
    'whiteSpace': 'normal',
    'height': 'auto',
    'font-family': 'Arial, sans-serif',
    'fontSize': '14px'
}

table_header_style = {
    'backgroundColor': 'rgb(230, 230, 230)',
    'fontWeight': 'bold',
    'borderBottom': '2px solid rgb(200, 200, 200)'
}

table_style = {
    'margin': '20px auto',
    'width': '90%',
    'boxShadow': '0 0 5px rgba(0,0,0,0.1)',
    'borderRadius': '5px'
}

table_conditional_style = [
    {
        'if': {'row_index': 'odd'},
        'backgroundColor': 'rgb(248, 248, 248)'
    }
]