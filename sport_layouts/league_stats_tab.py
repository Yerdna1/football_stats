from dash import html, dcc, dash_table

from league_names import LEAGUE_NAMES

from .utils import create_league_options
from .styles import table_cell_style, table_header_style, table_style
from .translations import get_translation as _  # Import translation function as _

def create_league_stats_tab():
    return dcc.Tab(label=_('League Statistics'), children=[
        html.H1(_("League Statistics Analysis"),
               style={'text-align': 'center', 'margin': '20px'}),
        
        # League selector
        html.Div([
            html.Label(_('Select League'),
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
                html.H3(_("Goal Statistics"), 
                        style={'text-align': 'center', 'color': '#2c3e50'}),
                html.Div([
                    html.P(_("Average Goals per Match:"), 
                           style={'font-weight': 'bold', 'margin': '5px 0'}),
                    html.Span(id='avg-goals-stat',
                             style={'font-size': '24px', 'color': '#e67e22'})
                ], style={'text-align': 'center', 'margin': '10px 0'})
            ], style={'width': '30%', 'display': 'inline-block', 'padding': '20px',
                     'box-shadow': '0 4px 8px 0 rgba(0,0,0,0.2)',
                     'margin': '10px', 'border-radius': '5px'}),
            
            # Average Yellow Cards Card
            html.Div([
                html.H3(_("Yellow Card Statistics"), 
                        style={'text-align': 'center', 'color': '#2c3e50'}),
                html.Div([
                    html.P(_("Average Yellow Cards per Match:"), 
                           style={'font-weight': 'bold', 'margin': '5px 0'}),
                    html.Span(id='avg-yellow-stat',
                             style={'font-size': '24px', 'color': '#f1c40f'})
                ], style={'text-align': 'center', 'margin': '10px 0'})
            ], style={'width': '30%', 'display': 'inline-block', 'padding': '20px',
                     'box-shadow': '0 4px 8px 0 rgba(0,0,0,0.2)',
                     'margin': '10px', 'border-radius': '5px'}),
            
            # Average Red Cards Card
            html.Div([
                html.H3(_("Red Card Statistics"), 
                        style={'text-align': 'center', 'color': '#2c3e50'}),
                html.Div([
                    html.P(_("Average Red Cards per Match:"), 
                           style={'font-weight': 'bold', 'margin': '5px 0'}),
                    html.Span(id='avg-red-stat',
                             style={'font-size': '24px', 'color': '#c0392b'})
                ], style={'text-align': 'center', 'margin': '10px 0'})
            ], style={'width': '30%', 'display': 'inline-block', 'padding': '20px',
                     'box-shadow': '0 4px 8px 0 rgba(0,0,0,0.2)',
                     'margin': '10px', 'border-radius': '5px'})
        ], style={'text-align': 'center', 'margin': '20px 0'}),
        
        # League Goals Comparison Chart
        html.Div([
            html.H2(_("Goals Comparison Across Leagues"),
                   style={'text-align': 'center', 'margin': '20px 0'}),
            
            # Add category selector for the charts
            html.Div([
                html.Label(_('View'),
                          style={'display': 'inline-block', 'margin-right': '10px', 'font-weight': 'bold'}),
                dcc.RadioItems(
                    id='league-category-selector',
                    options=[
                        {'label': _('All Categories'), 'value': 'all'},
                        {'label': _('Top Leagues'), 'value': 'top'},
                        {'label': _('Mid-Tier Leagues'), 'value': 'middle'},
                        {'label': _('Bottom Leagues'), 'value': 'bottom'}
                    ],
                    value='all',
                    inline=True,
                    style={'display': 'inline-block'}
                )
            ], style={'text-align': 'center', 'margin': '10px 0'}),
            
            # Container for selected visualization
            html.Div(id='league-goals-visualization-container')
            
        ], style={'margin': '20px 0'}),
        
        # Common Results Table
        html.Div([
            html.H2(_("Most Common Results"),
                   style={'text-align': 'center', 'margin': '20px 0'}),
            dash_table.DataTable(
                id='common-results-table',
                columns=[
                    {'name': _('Result'), 'id': 'result'},
                    {'name': _('Count'), 'id': 'count'},
                    {'name': _('Percentage'), 'id': 'percentage'}
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
