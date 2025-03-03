from dash import html, dcc, dash_table

from league_names import LEAGUE_NAMES

from .utils import create_league_options
from .styles import table_cell_style, table_header_style, table_style
from .translations import get_translation as _  # Import translation function if needed

def preprocess_form_data(data):
    """
    Preprocesses the 'form' column into a list of HTML spans for conditional formatting.
    Make sure to use 'presentation': 'html' for the form column in the DataTable.
    """
    for row in data:
        form = row.get("form", "")
        styled_form = ""
        for char in form:
            if char == "W":
                styled_form += f"<span style='display:inline-block; background-color:#4CAF50; color:white; padding:3px 6px; margin:2px; border-radius:4px; font-weight:bold;'>{char}</span>"
            elif char == "L":
                styled_form += f"<span style='display:inline-block; background-color:#F44336; color:white; padding:3px 6px; margin:2px; border-radius:4px; font-weight:bold;'>{char}</span>"
            elif char == "D":
                styled_form += f"<span style='display:inline-block; background-color:#FFC107; color:#333; padding:3px 6px; margin:2px; border-radius:4px; font-weight:bold;'>{char}</span>"
            else:
                styled_form += f"<span style='display:inline-block; margin:2px;'>{char}</span>"
        row["form"] = styled_form
    return data

# Enhanced styles
card_style = {
    'boxShadow': '0 4px 8px 0 rgba(0,0,0,0.2)',
    'borderRadius': '8px',
    'backgroundColor': 'white',
    'padding': '20px',
    'margin': '15px 0',
}

header_style = {
    'textAlign': 'center',
    'color': '#2C3E50',
    'fontFamily': 'Arial, sans-serif',
    'fontWeight': 'bold',
    'margin': '10px 0 20px 0',
    'padding': '5px',
    'borderBottom': '2px solid #3498DB',
}

subheader_style = {
    'textAlign': 'center',
    'color': '#34495E',
    'fontFamily': 'Arial, sans-serif',
    'margin': '15px 0',
    'padding': '5px',
}

# Enhanced table styles
enhanced_table_style = {
    'overflowX': 'auto',
    'width': '100%',
    'margin': '10px auto',
    'borderRadius': '5px',
    'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
}

enhanced_header_style = {
    'backgroundColor': '#3498DB',
    'color': 'white',
    'fontWeight': 'bold',
    'textAlign': 'center',
    'padding': '12px',
    'borderBottom': '1px solid #ddd'
}

enhanced_cell_style = {
    'textAlign': 'center',
    'padding': '10px',
    'fontFamily': 'Arial, sans-serif',
    'borderBottom': '1px solid #ddd'
}

def create_form_analysis_tab():
    return dcc.Tab(
        label='Analýza formy', 
        style={
            'fontWeight': 'bold',
            'backgroundColor': '#f8f9fa',
            'borderRadius': '5px 5px 0 0',
        },
        selected_style={
            'fontWeight': 'bold',
            'backgroundColor': '#3498DB',
            'color': 'white',
            'borderRadius': '5px 5px 0 0',
        },
        children=[
            # Main container with background
            html.Div(style={
                'backgroundColor': '#f5f8fa',
                'padding': '20px',
                'minHeight': '100vh',
            }, children=[
                # Header section
                html.Div(style=card_style, children=[
                    html.H1("Analýza formy tímov", style={
                        'textAlign': 'center',
                        'color': '#2C3E50',
                        'fontSize': '32px',
                        'margin': '10px 0 20px 0',
                        'fontFamily': 'Arial, sans-serif'
                    }),
                    
                    # Controls section with flexbox
                    html.Div(style={
                        'display': 'flex',
                        'flexWrap': 'wrap',
                        'justifyContent': 'space-around',
                        'alignItems': 'flex-start',
                        'margin': '20px 0',
                    }, children=[
                        # League selector
                        html.Div(style={
                            'width': '45%',
                            'minWidth': '300px',
                            'margin': '10px',
                            'padding': '15px',
                            'backgroundColor': 'white',
                            'borderRadius': '8px',
                            'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                        }, children=[
                            html.Label('Vybrať ligu', style={
                                'display': 'block',
                                'margin': '0 0 10px 0',
                                'textAlign': 'center',
                                'fontSize': '16px',
                                'fontWeight': 'bold',
                                'color': '#2C3E50'
                            }),
                            dcc.Dropdown(
                                id='form-league-dropdown',
                                options=create_league_options(LEAGUE_NAMES),
                                value=39,
                                style={
                                    'width': '100%',
                                    'boxShadow': '0 1px 3px rgba(0,0,0,0.1)',
                                    'borderRadius': '4px',
                                }
                            )
                        ]),
                        
                        # Form length selector
                        html.Div(style={
                            'width': '45%',
                            'minWidth': '300px',
                            'margin': '10px',
                            'padding': '15px',
                            'backgroundColor': 'white',
                            'borderRadius': '8px',
                            'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                        }, children=[
                            html.Label('Dĺžka analýzy formy', style={
                                'display': 'block',
                                'margin': '0 0 10px 0',
                                'textAlign': 'center',
                                'fontSize': '16px',
                                'fontWeight': 'bold',
                                'color': '#2C3E50'
                            }),
                            dcc.RadioItems(
                                id='form-length-selector',
                                options=[
                                    {'label': 'Posledné 3 zápasy', 'value': 3},
                                    {'label': 'Posledných 5 zápasov', 'value': 5}
                                ],
                                value=3,
                                inline=True,
                                style={
                                    'display': 'flex',
                                    'justifyContent': 'space-around',
                                    'padding': '10px',
                                    'backgroundColor': '#f8f9fa',
                                    'borderRadius': '4px',
                                }
                            )
                        ]),
                    ]),
                ]),

                # Form Analysis Table Section
                html.Div(style=card_style, children=[
                    html.H2("Analýza formy vs aktuálny výkon", style=header_style),
                    dash_table.DataTable(
                        id='form-analysis-table',
                        columns=[
                            {'name': 'Tím', 'id': 'team'},
                            {'name': 'Liga', 'id': 'league'},
                            {'name': 'Aktuálna pozícia', 'id': 'current_position'},
                            {'name': 'Body', 'id': 'current_points'},
                            {'name': 'Priemer bodov', 'id': 'current_ppg'},
                            {'name': 'Aktuálna forma', 'id': 'form', 'presentation': 'html'},
                            {'name': 'Body z formy', 'id': 'form_points'},
                            {'name': 'Priemer bodov z formy', 'id': 'form_ppg'},
                            {'name': 'Rozdiel výkonu', 'id': 'performance_diff'},
                            {'name': 'Zranení hráči', 'id': 'injured_players'}
                        ],
                        style_cell=enhanced_cell_style,
                        style_header=enhanced_header_style,
                        style_table=enhanced_table_style,
                        data=[],
                        # Allow HTML content
                        dangerously_allow_html=True,
                        style_data_conditional=[
                            {
                                'if': {'column_id': 'performance_diff', 'filter_query': '{performance_diff} > 0'},
                                'color': '#4CAF50',
                                'fontWeight': 'bold'
                            },
                            {
                                'if': {'column_id': 'performance_diff', 'filter_query': '{performance_diff} < 0'},
                                'color': '#F44336',
                                'fontWeight': 'bold'
                            },
                            {
                                'if': {'column_id': 'injured_players'},
                                'color': '#F44336'
                            },
                            {
                                'if': {'row_index': 'odd'},
                                'backgroundColor': '#f8f9fa'
                            }
                        ],
                        style_as_list_view=True,
                        page_action='native',
                        page_size=10,
                        filter_action='native',
                        sort_action='native',
                    )
                ]),
                        
                # Squad Statistics section
                html.Div(style=card_style, children=[
                    html.H2("Analýza štatistík hráčov", style=header_style),
                    
                    # Team selector in a nice card
                    html.Div(style={
                        'backgroundColor': '#f8f9fa',
                        'padding': '15px',
                        'borderRadius': '8px',
                        'margin': '15px auto',
                        'width': '80%',
                        'maxWidth': '600px',
                    }, children=[
                        html.Label('Vybrať tím', style={
                            'display': 'block',
                            'margin': '0 0 10px 0',
                            'textAlign': 'center',
                            'fontSize': '16px',
                            'fontWeight': 'bold',
                            'color': '#2C3E50'
                        }),
                        dcc.Dropdown(
                            id='team-selector-dropdown',
                            placeholder='Vyberte tím pre zobrazenie štatistík',
                            style={
                                'width': '100%',
                                'boxShadow': '0 1px 3px rgba(0,0,0,0.1)',
                                'borderRadius': '4px',
                            }
                        )
                    ]),
                    
                    # Stats type selector styled as tabs
                    html.Div(style={
                        'textAlign': 'center',
                        'margin': '20px 0',
                    }, children=[
                        dcc.RadioItems(
                            id='stats-type-selector',
                            options=[
                                {'label': 'Základné štatistiky', 'value': 'basic'},
                                {'label': 'Pokročilé štatistiky', 'value': 'advanced'}
                            ],
                            value='basic',
                            inline=True,
                            labelStyle={
                                'display': 'inline-block',
                                'margin': '0 10px',
                                'padding': '10px 20px',
                                'backgroundColor': '#e9ecef',
                                'borderRadius': '20px',
                                'cursor': 'pointer',
                            },
                            style={
                                'backgroundColor': 'white',
                                'padding': '10px',
                                'borderRadius': '8px',
                            }
                        )
                    ]),

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
                                style_cell=enhanced_cell_style,
                                style_header=enhanced_header_style,
                                style_table=enhanced_table_style,
                                style_data_conditional=[
                                    {
                                        'if': {'row_index': 'odd'},
                                        'backgroundColor': '#f8f9fa'
                                    }
                                ],
                                page_size=10,
                                sort_action='native',
                                filter_action='native',
                                style_as_list_view=True,
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
                                style_cell=enhanced_cell_style,
                                style_header=enhanced_header_style,
                                style_table=enhanced_table_style,
                                style_data_conditional=[
                                    {
                                        'if': {'row_index': 'odd'},
                                        'backgroundColor': '#f8f9fa'
                                    }
                                ],
                                page_size=10,
                                sort_action='native',
                                filter_action='native',
                                style_as_list_view=True,
                            )
                        ],
                        style={'display': 'none'}
                    )
                ]),

                # Upcoming Fixtures Table
                html.Div(style=card_style, children=[
                    html.H2("Nadchádzajúce zápasy pre tímy s najväčšími zmenami formy", style=header_style),
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
                        style_cell=enhanced_cell_style,
                        style_header=enhanced_header_style,
                        style_table=enhanced_table_style,
                        data=[],
                        style_data_conditional=[
                            {
                                'if': {'column_id': 'performance_diff', 'filter_query': '{performance_diff} > 0'},
                                'color': '#4CAF50',
                                'fontWeight': 'bold'
                            },
                            {
                                'if': {'column_id': 'performance_diff', 'filter_query': '{performance_diff} < 0'},
                                'color': '#F44336',
                                'fontWeight': 'bold'
                            },
                            {
                                'if': {'row_index': 'odd'},
                                'backgroundColor': '#f8f9fa'
                            }
                        ],
                        page_size=10,
                        sort_action='native',
                        filter_action='native',
                        style_as_list_view=True,
                    )
                ])
            ])
        ]
    )
