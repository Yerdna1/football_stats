from dash import html, dcc, dash_table
from config import LEAGUE_NAMES
from .utils import create_league_options
from .styles import table_cell_style, table_header_style, table_style, table_conditional_style

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
    
def create_winless_streaks_tab():
    return dcc.Tab(label='Winless Streaks', children=[
        html.H1("Winless Streaks in Top 5 European Leagues", 
               style={'text-align': 'center', 
                     'margin-bottom': '30px',
                     'margin-top': '20px',
                     'font-family': 'Arial, sans-serif'}),
        dcc.Dropdown(
            id='winless-league-dropdown',
            options=create_league_options(LEAGUE_NAMES),
            value=39,
            style={'width': '80%', 
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