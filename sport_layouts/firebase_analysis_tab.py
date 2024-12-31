from dash import html, dcc, dash_table

from config import LEAGUE_NAMES
from .utils import create_league_options
from .styles import table_cell_style, table_header_style, table_style

def create_firebase_analysis_tab():
    return dcc.Tab(
        label='Firebase Analysis',
        value='firebase-analysis-tab',
        children=[
            html.Div([
                # Controls
                html.Div([
                    html.Button(
                        'Analyze Data',
                        id='analyze-data-button',
                        className='button-primary mr-2 mb-4'
                    ),
                    html.Button(
                        'Force Refresh',
                        id='force-refresh-button',
                        className='button-secondary mb-4'
                    ),
                ], className='flex space-x-4'),
                
                # Cache Info
                html.Div(id='cache-info', className='mb-4'),
                
                # Data Quality Section
                html.Div([
                    html.H2("Data Quality Analysis", className='text-2xl font-bold mb-4'),
                    html.Div(id='data-quality-container')
                ], className='mb-8'),
                
                # Player Statistics Section
                html.Div([
                    html.H2("Player Statistics", className='text-2xl font-bold mb-4'),
                    html.Div(id='player-stats-container')
                ], className='mb-8'),
                
                # Team Statistics Section
                html.Div([
                    html.H2("Team Statistics", className='text-2xl font-bold mb-4'),
                    html.Div(id='team-stats-container')
                ])
            ], className='p-4')
        ]
    )