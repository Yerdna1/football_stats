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
    return dcc.Tab(label='Analýza formy', children=[
        html.H1("Analýza formy tímov",
                style={'text-align': 'center', 'margin': '20px'}),

        # League selector
        html.Div([
            html.Label('Vybrať ligu',
                     style={'display': 'block', 'margin-bottom': '5px', 'text-align': 'center'}),
            dcc.Dropdown(
                id='form-league-dropdown',
                options=create_league_options(LEAGUE_NAMES),
                value=39,
                style={'width': '100%', 'box-shadow': '0 2px 4px rgba(0,0,0,0.1)'}
            )
        ], style={'width': '80%', 'margin': '20px auto'}),

        # Form length selector
        html.Div([
            html.Label('Dĺžka analýzy formy',
                     style={'display': 'block', 'margin-bottom': '5px', 'text-align': 'center'}),
            dcc.RadioItems(
                id='form-length-selector',
                options=[
                    {'label': 'Posledné 3 zápasy', 'value': 3},
                    {'label': 'Posledných 5 zápasov', 'value': 5}
                ],
                value=3,
                inline=True,
                style={'width': '80%', 'margin': '20px auto', 'backgroundColor': '#FFFFFF', 'padding': '15px', 'borderRadius': '8px'}
            )
        ], style={'width': '80%', 'margin': '20px auto'}),

        # Form Analysis Table
        html.Div([
            html.H2("Analýza formy vs aktuálny výkon",
                   style={'text-align': 'center', 'margin': '20px 0'}),
            dash_table.DataTable(
                id='form-analysis-table',
                columns=[
                    {'name': 'Tím', 'id': 'team'},
                    {'name': 'Liga', 'id': 'league'},
                    {'name': 'Aktuálna pozícia', 'id': 'current_position'},
                    {'name': 'Body', 'id': 'current_points'},
                    {'name': 'Priemer bodov', 'id': 'current_ppg'},
                    {'name': 'Aktuálna forma', 'id': 'form', 'presentation': 'markdown'},
                    {'name': 'Body z formy', 'id': 'form_points'},
                    {'name': 'Priemer bodov z formy', 'id': 'form_ppg'},
                    {'name': 'Rozdiel výkonu', 'id': 'performance_diff'},
                    {'name': 'Zranení hráči', 'id': 'injured_players'}
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
        ]),
                
        # Squad Statistics section
        html.Div([
            html.H2("Analýza štatistík hráčov",
                   style={'text-align': 'center', 'margin': '20px 0'}),
            
            # Add team selector
            html.Div([
                html.Label('Vybrať tím',
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
                    {'label': 'Základné štatistiky', 'value': 'basic'},
                    {'label': 'Pokročilé štatistiky', 'value': 'advanced'}
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
                            {'name': 'Hráč', 'id': 'name'},
                            {'name': 'Pozícia', 'id': 'position'},
                            {'name': 'Vek', 'id': 'age'},
                            {'name': 'Zápasy', 'id': 'appearances'},
                            {'name': 'Minúty', 'id': 'minutes'},
                            {'name': 'Góly', 'id': 'goals'},
                            {'name': 'Asistencie', 'id': 'assists'},
                            {'name': 'Hodnotenie', 'id': 'rating'},
                            {'name': 'Žlté karty', 'id': 'yellow_cards'},
                            {'name': 'Červené karty', 'id': 'red_cards'}
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
                            {'name': 'Hráč', 'id': 'name'},
                            {'name': 'Pozícia', 'id': 'position'},
                            {'name': 'Strely celkom', 'id': 'shots_total'},
                            {'name': 'Strely na bránu', 'id': 'shots_on'},
                            {'name': 'Presnosť prihrávok %', 'id': 'passes_accuracy'},
                            {'name': 'Kľúčové prihrávky', 'id': 'passes_key'},
                            {'name': 'Sklzy', 'id': 'tackles'},
                            {'name': 'Zachytenia', 'id': 'interceptions'},
                            {'name': 'Dribling (Ú/P)', 'id': 'dribbles_success'},
                            {'name': 'Vynútené fauly', 'id': 'fouls_drawn'}
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
        ], style={'margin': '20px 0'}),

        # Upcoming Fixtures Table
        html.Div([
            html.H2("Nadchádzajúce zápasy pre tímy s najväčšími zmenami formy",
                   style={'text-align': 'center', 'margin': '30px 0 20px 0'}),
            dash_table.DataTable(
                id='upcoming-fixtures-table',
                columns=[
                    {'name': 'Tím', 'id': 'team'},
                    {'name': 'Rozdiel výkonu', 'id': 'performance_diff'},
                    {'name': 'Nasledujúci súper', 'id': 'next_opponent'},
                    {'name': 'Dátum', 'id': 'date'},
                    {'name': 'Čas', 'id': 'time'},
                    {'name': 'Miesto', 'id': 'venue'}
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
                    }
                ]
            )
        ])
    ])
