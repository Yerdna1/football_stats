import base64
from collections import defaultdict
import io
import logging
from typing import Dict
from venv import logger
import dash
from dash.dependencies import Input, Output, State
from dash import html, dash_table, dcc
from datetime import datetime
import pandas as pd
import plotly.express as px
from config import ALL_LEAGUES, LEAGUE_NAMES
from sport_analyzers import LeagueAnalyzer
from dash import html, dcc, ctx
from dash.exceptions import PreventUpdate  # Import PreventUpdate
from sport_analyzers.firebase_analyzer import analyze_data_quality, create_data_quality_report, create_player_statistics, create_player_statistics_table
from sport_callbacks.fixtures_tab_data_collection_callback import RateLimiter, make_api_request
import time
from google.api_core.exceptions import ServiceUnavailable
from dash import html, dcc, dash_table
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

# Configure logger (consider moving this to a central logging setup)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Set the logger level to DEBUG
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


def fetch_fixtures_with_retry(db, collection_name='fixtures', batch_size=500, retries=3, delay=5):
    """
    Fetches data from a Firestore collection with retry logic and pagination.

    Args:
        db: Firestore database client.
        collection_name: Name of the Firestore collection to fetch from (default is 'fixtures').
        batch_size: Number of documents to fetch per batch (default is 500).
        retries: Maximum number of retry attempts in case of ServiceUnavailable errors (default is 3).
        delay: Time in seconds to wait between retries (default is 5).

    Returns:
        list: A list of dictionaries representing the fetched documents.

    Raises:
        ServiceUnavailable: If the service is unavailable after the maximum number of retries.
        Exception: For any other errors that occur during the fetching.
    """
    all_documents = []
    start_after = None
    attempt = 0
    logger.debug("Starting fetch_fixtures_with_retry function")


    while True:
        try:
            logger.debug(f"Attempting to fetch documents (batch), try {attempt + 1} of {retries}")
            query = db.collection(collection_name).order_by("__name__").limit(batch_size)

            if start_after:
                query = query.start_after(start_after)
            
            logger.debug(f"Firestore query created {query}")


            docs = list(query.stream())
            documents_data = [doc.to_dict() for doc in docs]
            logger.debug(f"Fetched {len(documents_data)} from firestore")

            
            if not documents_data:
                logger.debug("No more documents found, exiting loop")
                break  # No more documents, exit the loop

            all_documents.extend(documents_data)  # Add current batch to the accumulated list
            if docs:
                start_after = docs[-1]  # Setup pagination for the next iteration
            
            attempt = 0  # Reset attempt counter
            logger.info(f"Fetched {len(documents_data)} documents in this batch. Total fetched: {len(all_documents)}")


        except ServiceUnavailable as e:
            attempt += 1
            logger.error(f"ServiceUnavailable error during query attempt {attempt}: {e}")
            if attempt < retries:
                logger.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                logger.error("Max retries reached for batch, failing the operation.")
                raise  # Re-raise the exception if retries failed
        except Exception as e:
            logger.error(f"Error fetching documents: {e}", exc_info=True)
            raise # Raise an exception if there is any other error

    logger.info(f"Fetched total of {len(all_documents)} documents from collection: {collection_name}")
    logger.debug("Finished fetch_fixtures_with_retry function")
    return all_documents




def parse_csv_content(contents, filename):
    logger.debug("Starting parse_csv_content")
    try:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        
        # Handle Excel files
        if 'excel' in content_type.lower():
            return pd.read_excel(
                io.BytesIO(decoded),
                engine='openpyxl',
                sheet_name=0  # First sheet
            )
        # Handle CSV
        else:
            return pd.read_csv(
                io.BytesIO(decoded),
                encoding='utf-8-sig',
                on_bad_lines='skip'
            )
            
    except Exception as e:
        logger.error(f"Error parsing file: {str(e)}")
        logger.debug(f"Content type: {content_type}")
        return None




def analyze_csv_data(df):
    """Analyze CSV data using same logic as Firebase analysis"""
    try:
        if df is None:
            return None

        stats = {
            'total_fixtures': len(df),
            'leagues': defaultdict(lambda: {
                'fixtures_count': 0,
                'seasons': set(),
                'teams': set(),
                'players': set(),
                'complete_data': 0,
                'missing_data': 0
            })
        }

        # Apply similar analysis logic as in analyze_data_quality()
        for _, row in df.iterrows():
            try:
                league_id = str(row.get('league_id', ''))
                if not league_id:
                    continue

                stats['leagues'][league_id]['fixtures_count'] += 1
                stats['leagues'][league_id]['seasons'].add(str(row.get('season', '')))
                
                # Add team data
                home_team = row.get('home_team_id')
                away_team = row.get('away_team_id')
                if home_team:
                    stats['leagues'][league_id]['teams'].add(str(home_team))
                if away_team:
                    stats['leagues'][league_id]['teams'].add(str(away_team))

            except Exception as e:
                logger.error(f"Error processing CSV row: {e}", exc_info=True)
                continue

        return stats
    except Exception as e:
        logger.error(f"Error analyzing CSV data: {e}", exc_info=True)
        return None


def setup_firebase_analysis_callbacks(app, db):
    @app.callback(
        [Output('player-stats-container', 'children'),
         Output('firebase-error-container', 'children')],
        [Input('analyze-data-button', 'n_clicks'),
         Input('csv-upload', 'contents')],
        [State('csv-upload', 'filename')],
        prevent_initial_call=True
    )
    def update_analysis(n_clicks,  contents, filename):
        ctx=dash.callback_context
        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
        logger.debug("Starting update_analysis callback")
        if not n_clicks:
            logger.debug("PreventUpdate triggered, n_clicks is None")
            raise PreventUpdate
        

        if triggered_id == 'analyze-data-button':
            try:
                    logger.debug("Starting Firebase data analysis process")
                    quality_stats = analyze_data_quality(db)
                    logger.debug("Finished analyze_data_quality")
                    fixtures_data = fetch_fixtures_with_retry(db)
                    logger.debug(f"Finished fetch_fixtures_with_retry, {len(fixtures_data)} documents were fetched")


                    quality_report = create_data_quality_report(quality_stats)
                    logger.debug("Finished create_data_quality_report")
                    player_stats = create_player_statistics(fixtures_data)
                    logger.debug("Finished create_player_statistics")
                    player_df = create_player_statistics_table(player_stats)  # Create DataFrame
                    logger.debug("Finished create_player_statistics_table")


                    # Enable CSV download for the player stats table
                    download_button = dcc.Download(
                        id='download-player-stats',
                        data=player_df.to_csv(index=False),  # Convert DataFrame to CSV
                        type="text/csv",
                    )

                    player_table = dash_table.DataTable(
                        columns=[{"name": col, "id": col} for col in player_df.columns],
                        data=player_df.to_dict('records'),
                        style_cell={'overflow': 'hidden', 'textOverflow': 'ellipsis'},
                        style_header={'backgroundColor': 'lightblue', 'fontWeight': 'bold'},
                        style_data={'backgroundColor': 'lavender'},
                        export_format='csv',  # Enable built-in export (optional)
                        export_headers=True,  # Include headers in the exported CSV (optional)
                        page_size=20,
                    )
                    logger.debug("Finished creating player table")

                    logger.debug("Finished Firebase data analysis process successfully")
                    return html.Div([quality_report, download_button, player_table]), None

            except Exception as e:
                logger.error(f"Error in analysis: {e}", exc_info=True)
                return  None,  html.Div(f"Error: {str(e)}")
        elif triggered_id == 'csv-upload' and contents:
            try:
                df = parse_csv_content(contents)
                numeric_analysis = df.describe()
                
                analysis_table = dash_table.DataTable(
                    columns=[{"name": col, "id": col} for col in numeric_analysis.columns],
                    data=numeric_analysis.to_dict('records'),
                    style_cell={'textAlign': 'left', 'padding': '10px'},
                    style_header={'backgroundColor': 'rgb(230, 230, 230)'}
                )
                
                return dash.no_update, analysis_table
            except Exception as e:
                logger.error(f"Error in analysis: {e}", exc_info=True)
                return  None,  html.Div(f"Error: {str(e)}")

        raise PreventUpdate
    @app.callback(
    [Output('csv-data-quality', 'children'),
     Output('csv-player-stats', 'children'),
     Output('csv-error-container', 'children')],
    [Input('analyze-csv-button', 'n_clicks')],
    [State('csv-upload', 'contents'),
     State('csv-upload', 'filename')]
    )
    def update_csv_analysis(n_clicks, contents, filename):
        if not contents:
            raise PreventUpdate
            
        df = parse_csv_content(contents, filename)
        if df is None:
            return None, None, "Error parsing CSV file"
            
        return analyze_csv_data(df)
                