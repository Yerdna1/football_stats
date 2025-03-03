import logging
from dash import html, dcc, dash_table

from .utils import create_league_options
from .styles import table_cell_style, table_header_style, table_style
from .translations import get_translation as _  # Import translation function as _

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

def create_firebase_analysis_tab():
    """
    Create the Firebase Analysis tab with data quality, player statistics, CSV analysis, and team sections.
    """
    logger.debug("Starting create_firebase_analysis_tab function")
    try:
        tab = dcc.Tab(
            label=_('Firebase Analysis'),
            value='firebase-analysis-tab',
            children=[
                # Firebase Analysis Section
                html.Div([
                    # Analyze Data Button
                    html.Button(
                        _('Analyze Data'),
                        id='analyze-data-button',
                        className='button-primary mb-4'
                    ),
                    
                    # Data Quality Section
                    html.Div([
                        html.H2(_("Data Quality Analysis"), className='text-2xl font-bold mb-4'),
                        html.Div(id='data-quality-container')
                    ], className='mb-8'),

                    # Player Statistics Section
                    html.Div([
                        html.H2(_("Player Statistics"), className='text-2xl font-bold mb-4'),
                        html.Div(id='player-stats-container'),
                        html.Div(id='firebase-error-container'),
                    ], className='mb-8'),

                    # Team Statistics Section
                    html.Div([
                        html.H2(_("Team Statistics"), className='text-2xl font-bold mb-4'),
                        dash_table.DataTable(
                            id='team-statistics-table',
                            columns=[],  # Columns will be populated dynamically
                            data=[],     # Data will be populated dynamically
                            filter_action='native',
                            sort_action='native',
                            page_action='native',
                            page_size=20,
                            style_table={'overflowX': 'auto'},
                            style_cell=table_cell_style,
                            style_header=table_header_style,
                        )
                    ], className='mb-8'),

                    # Team Quality Report Section
                    html.Div([
                        html.H2(_("Team Quality Report"), className='text-2xl font-bold mb-4'),
                        dash_table.DataTable(
                            id='team-quality-report-table',
                            columns=[],  # Columns will be populated dynamically
                            data=[],     # Data will be populated dynamically
                            filter_action='native',
                            sort_action='native',
                            page_action='native',
                            page_size=20,
                            style_table={'overflowX': 'auto'},
                            style_cell=table_cell_style,
                            style_header=table_header_style,
                        )
                    ], className='mb-8'),

                    # Team Report Section
                    html.Div([
                        html.H2(_("Team Report"), className='text-2xl font-bold mb-4'),
                        dash_table.DataTable(
                            id='team-report-table',
                            columns=[],  # Columns will be populated dynamically
                            data=[],     # Data will be populated dynamically
                            filter_action='native',
                            sort_action='native',
                            page_action='native',
                            page_size=20,
                            style_table={'overflowX': 'auto'},
                            style_cell=table_cell_style,
                            style_header=table_header_style,
                        )
                    ], className='mb-8'),


                    
                    # Team Statistics Section (Note: This appears to be duplicate)
                    html.Div([
                        html.H2(_("Team Statistics"), className='text-2xl font-bold mb-4'),
                        html.Div(id='team-stats-container')
                    ], className='mb-8')
                ], className='p-4'),
            
            ]
        )
        logger.debug("Finished create_firebase_analysis_tab function")
        return tab
    except Exception as e:
        logger.error(f"Error creating firebase analysis tab: {e}", exc_info=True)
        return html.Div(_("Error creating firebase tab"))
