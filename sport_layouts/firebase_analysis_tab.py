import logging
from dash import html, dcc, dash_table

from config import LEAGUE_NAMES
from .utils import create_league_options
from .styles import table_cell_style, table_header_style, table_style

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

def create_firebase_analysis_tab():
    logger.debug("Starting create_firebase_analysis_tab function")
    try:
        tab = dcc.Tab(
            label='Firebase Analysis',
            value='firebase-analysis-tab',
            children=[

                html.Div([
                    html.Button(
                        'Analyze Data',
                        id='analyze-data-button',
                        className='button-primary mb-4'
                    ),
          
                    
                    
                    # Data Quality Section
                    html.Div([
                        html.H2("Data Quality Analysis", className='text-2xl font-bold mb-4'),
                        html.Div(id='data-quality-container')
                    ], className='mb-8'),
                    
                    # Player Statistics Section
                    html.Div([
                        html.H2("Player Statistics", className='text-2xl font-bold mb-4'),
                        html.Div(id='player-stats-container'),
                          html.Div(id='firebase-error-container'),
                    ])
                ], className='p-4'),


                # CSV Analysis Section
                html.Div([
                    html.H2("CSV Analysis", className='text-2xl font-bold mb-4'),
                    dcc.Upload(
                        id='csv-upload',
                        children=html.Div([
                            'Drag and Drop or ',
                            html.A('Select CSV File')
                        ]),
                        style={
                            'width': '100%',
                            'height': '60px',
                            'lineHeight': '60px',
                            'borderWidth': '1px',
                            'borderStyle': 'dashed',
                            'borderRadius': '5px',
                            'textAlign': 'center',
                            'margin': '10px 0'
                        }
                    ),
                    html.Button(
                        'Analyze CSV Data',
                        id='analyze-csv-button',
                        className='button-primary mb-4',
                        style={'margin': '10px 0'}
                    ),
                    html.Div([
                        html.Div(id='csv-data-quality'),
                        html.Div(id='csv-player-stats'),
                        html.Div(id='csv-error-container')
                    ])
                ], className='p-4')

            ]
        )
        logger.debug("Finished create_firebase_analysis_tab function")
        return tab
    except Exception as e:
        logger.error(f"Error creating firebase analysis tab: {e}", exc_info=True)
        return html.Div("Error creating firebase tab")