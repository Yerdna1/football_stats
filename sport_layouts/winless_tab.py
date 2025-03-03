from dash import html, dcc, dash_table
from league_names import LEAGUE_NAMES
from .utils import create_league_options
from .styles import table_cell_style, table_header_style, table_style, table_conditional_style

def create_last_matches_table():
    return html.Div([
        html.H2("Posledné výsledky pre 5 najhorších tímov bez výhry",
               style={'text-align': 'center',
                     'margin': '20px 0',
                     'font-family': 'Arial, sans-serif'}),
        dash_table.DataTable(
            id='last-matches-table',
            columns=[
                {'name': 'Tím', 'id': 'team'},
                {'name': 'Séria bez výhry', 'id': 'streak'},
                {'name': 'Výsledok posledného zápasu', 'id': 'result'},
                {'name': 'Skóre', 'id': 'score'},
                {'name': 'Dátum', 'id': 'date'}
            ],
            style_cell=table_cell_style,
            style_header=table_header_style,
            style_table=table_style,
            style_data_conditional=table_conditional_style
        )
    ])
    
def create_winless_streaks_tab():
    return dcc.Tab(label='Série bez výhry', children=[
        html.H1("Série bez výhry v 5 najlepších európskych ligách", 
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
                options=[{'label': 'Zobraziť iba aktuálne prebiehajúce série', 
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
