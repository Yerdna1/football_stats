from dash import html, dcc, dash_table
from config import LEAGUE_NAMES
from .utils import create_league_options
from .styles import table_cell_style, table_header_style, table_style

def create_league_stats_tab():
    return dcc.Tab(label='League Statistics', children=[
        
        # League Goals Comparison Chart
        html.Div([
            html.H2("Goals Comparison Across Leagues",
                   style={'text-align': 'center', 'margin': '20px 0'}),
            dcc.Graph(id='league-goals-comparison')
        ], style={'margin': '20px 0'}),
        html.H1("League Statistics Analysis",
               style={'text-align': 'center', 'margin': '20px'}),
        
        html.H1("League Statistics Analysis",
               style={'text-align': 'center', 'margin': '20px'}),
        
        # League selector
        html.Div([
            html.Label('Select League',
                      style={'display': 'block', 'margin-bottom': '5px', 'text-align': 'center'}),
            dcc.Dropdown(
                id='stats-league-dropdown',
                options=create_league_options(LEAGUE_NAMES),
                value=39,
                style={'width': '100%'}
            )
        ], style={'width': '80%', 'margin': '20px auto'}),
        
        # Statistics Cards
        html.Div([
            # Average Goals Card
            html.Div([
                html.H3("Goal Statistics", 
                        style={'text-align': 'center', 'color': '#2c3e50'}),
                html.Div([
                    html.P("Average Goals per Match:", 
                           style={'font-weight': 'bold', 'margin': '5px 0'}),
                    html.Span(id='avg-goals-stat',
                             style={'font-size': '24px', 'color': '#e67e22'})
                ], style={'text-align': 'center', 'margin': '10px 0'})
            ], style={'width': '30%', 'display': 'inline-block', 'padding': '20px',
                     'box-shadow': '0 4px 8px 0 rgba(0,0,0,0.2)',
                     'margin': '10px', 'border-radius': '5px'}),
            
            # Average Yellow Cards Card
            html.Div([
                html.H3("Yellow Card Statistics", 
                        style={'text-align': 'center', 'color': '#2c3e50'}),
                html.Div([
                    html.P("Average Yellow Cards per Match:", 
                           style={'font-weight': 'bold', 'margin': '5px 0'}),
                    html.Span(id='avg-yellow-stat',
                             style={'font-size': '24px', 'color': '#f1c40f'})
                ], style={'text-align': 'center', 'margin': '10px 0'})
            ], style={'width': '30%', 'display': 'inline-block', 'padding': '20px',
                     'box-shadow': '0 4px 8px 0 rgba(0,0,0,0.2)',
                     'margin': '10px', 'border-radius': '5px'}),
            
            # Average Red Cards Card
            html.Div([
                html.H3("Red Card Statistics", 
                        style={'text-align': 'center', 'color': '#2c3e50'}),
                html.Div([
                    html.P("Average Red Cards per Match:", 
                           style={'font-weight': 'bold', 'margin': '5px 0'}),
                    html.Span(id='avg-red-stat',
                             style={'font-size': '24px', 'color': '#c0392b'})
                ], style={'text-align': 'center', 'margin': '10px 0'})
            ], style={'width': '30%', 'display': 'inline-block', 'padding': '20px',
                     'box-shadow': '0 4px 8px 0 rgba(0,0,0,0.2)',
                     'margin': '10px', 'border-radius': '5px'})
        ], style={'text-align': 'center', 'margin': '20px 0'}),
        
        # Common Results Table
        html.Div([
            html.H2("Most Common Results",
                   style={'text-align': 'center', 'margin': '20px 0'}),
            dash_table.DataTable(
                id='common-results-table',
                columns=[
                    {'name': 'Result', 'id': 'result'},
                    {'name': 'Count', 'id': 'count'},
                    {'name': 'Percentage', 'id': 'percentage'}
                ],
                style_cell=table_cell_style,
                style_header=table_header_style,
                style_table={'width': '60%', 'margin': '0 auto'},
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': '#f9f9f9'
                    }
                ]
            )
        ])
    ])