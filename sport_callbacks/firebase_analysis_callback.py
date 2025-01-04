import base64
from collections import defaultdict
import io
import logging
import os
from typing import Dict
from venv import logger
import dash
from dash.dependencies import Input, Output, State
from dash import html, dash_table, dcc
from datetime import datetime
import pandas as pd
import plotly.express as px
from config import ALL_LEAGUES
from sport_analyzers import LeagueAnalyzer
from dash import html, dcc, ctx
from dash.exceptions import PreventUpdate  # Import PreventUpdate
from sport_analyzers.TEAMS_STATS import analyze_team_data_quality_mod, create_team_report_mod, create_team_statistics_mod
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


def fetch_fixtures_with_retry(db, collection_name='fixtures', batch_size=1000, retries=3, delay=5):
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



def setup_firebase_analysis_callbacks(app, db):
    @app.callback(
    [Output('player-stats-container', 'children'),
     Output('data-quality-container', 'children'),
     Output('team-stats-container', 'children')],  # Add output for team stats
    Input('analyze-data-button', 'n_clicks'),
    prevent_initial_call=True
    )
    def update_analysis(n_clicks):
        ctx = dash.callback_context
        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
        logger.debug("Starting update_analysis callback")
        
        if not n_clicks:
            logger.debug("PreventUpdate triggered, n_clicks is None")
            raise PreventUpdate

        if triggered_id == 'analyze-data-button':
            try:
                logger.debug("Starting data analysis process")
                
                # Check if CSV files exist
                player_stats_csv_path = 'player_statistics.csv'
                data_quality_csv_path = 'data_quality_report.csv'
                team_stats_csv_path = 'team_statistics.csv'  # New CSV for team stats
                
                if os.path.exists(player_stats_csv_path) and os.path.exists(data_quality_csv_path) and os.path.exists(team_stats_csv_path):
                    logger.debug("CSV files found, loading data from CSVs")
                    
                    # Load player statistics from CSV
                    player_df = pd.read_csv(player_stats_csv_path)
                    logger.debug(f"Successfully loaded {len(player_df)} rows from {player_stats_csv_path}")
                    
                    # Load data quality report from CSV
                    data_quality_df = pd.read_csv(data_quality_csv_path)
                    logger.debug(f"Successfully loaded {len(data_quality_df)} rows from {data_quality_csv_path}")
                    
                    # Load team statistics from CSV
                    team_stats_df = pd.read_csv(team_stats_csv_path)
                    logger.debug(f"Successfully loaded {len(team_stats_df)} rows from {team_stats_csv_path}")
                    
                else:
                    logger.debug("CSV files not found, fetching data from Firebase")
                    
                    # Fetch data from Firebase
                    fixtures_data = fetch_fixtures_with_retry(db)
                    logger.debug(f"Fetched {len(fixtures_data)} documents from Firebase")
                    
                    # Analyze data quality
                    quality_stats = analyze_data_quality(fixtures_data)
                    logger.debug("Finished analyze_data_quality")
                    
                    # Create data quality report
                    quality_report, data_quality_df = create_data_quality_report(quality_stats)
                    logger.debug("Finished create_data_quality_report")
                    
                    # Create player statistics
                    player_stats = create_player_statistics(fixtures_data)
                    logger.debug("Finished create_player_statistics")
                    
                    # Create player statistics DataFrame
                    player_df = create_player_statistics_table(player_stats)
                    logger.debug("Finished create_player_statistics_table")
                    
                    # Create team statistics
                    team_stats = create_team_statistics_mod.create_team_statistics(fixtures_data)
                    logger.debug("Finished create_team_statistics")
                    
                    # Create team quality report
                    team_quality = analyze_team_data_quality_mod.analyze_team_data_quality(fixtures_data)
                    logger.debug("Finished analyze_team_data_quality")
                    
                    # Create team report
                    team_report, team_stats_df = create_team_report_mod.create_team_report(team_stats, team_quality)
                    logger.debug("Finished create_team_report")
                    
                    # Save team statistics to CSV
                    team_stats_df.to_csv(team_stats_csv_path, index=False)
                    logger.debug(f"Saved team statistics to {team_stats_csv_path}")

                # Debugging: Log data quality table data
                logger.debug(f"Data quality table columns: {data_quality_df.columns}")
                logger.debug(f"Data quality table data: {data_quality_df.to_dict('records')}")

                # Create player statistics table with pagination
                player_table = dash_table.DataTable(
                    id='player-stats-table',
                    columns=[{"name": col, "id": col} for col in player_df.columns],
                    data=player_df.to_dict('records'),
                    filter_action='native',  # Enable filtering
                    sort_action='native',    # Enable sorting
                    sort_mode='multi',       # Allow multi-column sorting
                    page_action='native',    # Enable pagination
                    page_size=20,            # Show 20 rows per page
                    persistence=True,        # Persist state
                    persistence_type='memory',  # Store state in memory
                    style_table={'overflowX': 'auto'},
                    style_cell={'textAlign': 'left', 'padding': '10px'},
                    style_header={
                        'backgroundColor': 'lightblue',
                        'fontWeight': 'bold'
                    },
                    style_data={'backgroundColor': 'lavender'},
                )
                logger.debug("Finished creating player statistics table")

                # Create data quality report table with pagination
                data_quality_table = dash_table.DataTable(
                    id='data-quality-table',
                    columns=[{"name": col, "id": col} for col in data_quality_df.columns],
                    data=data_quality_df.to_dict('records'),
                    filter_action='native',  # Enable filtering
                    sort_action='native',    # Enable sorting
                    sort_mode='multi',       # Allow multi-column sorting
                    page_action='native',    # Enable pagination
                    page_size=20,            # Show 20 rows per page
                    persistence=True,        # Persist state
                    persistence_type='memory',  # Store state in memory
                    style_table={'overflowX': 'auto'},
                    style_cell={'textAlign': 'left', 'padding': '10px'},
                    style_header={
                        'backgroundColor': 'lightblue',
                        'fontWeight': 'bold'
                    },
                    style_data={'backgroundColor': 'lavender'},
                )
                logger.debug("Finished creating data quality report table")

                # Create team statistics table with pagination
                team_stats_table = dash_table.DataTable(
                    id='team-stats-table',
                    columns=[{"name": col, "id": col} for col in team_stats_df.columns],
                    data=team_stats_df.to_dict('records'),
                    filter_action='native',  # Enable filtering
                    sort_action='native',    # Enable sorting
                    sort_mode='multi',       # Allow multi-column sorting
                    page_action='native',    # Enable pagination
                    page_size=20,            # Show 20 rows per page
                    persistence=True,        # Persist state
                    persistence_type='memory',  # Store state in memory
                    style_table={'overflowX': 'auto'},
                    style_cell={'textAlign': 'left', 'padding': '10px'},
                    style_header={
                        'backgroundColor': 'lightblue',
                        'fontWeight': 'bold'
                    },
                    style_data={'backgroundColor': 'lavender'},
                )
                logger.debug("Finished creating team statistics table")

                # Enable CSV download for the player stats table
                player_download_button = dcc.Download(
                    id='download-player-stats',
                    data=player_df.to_csv(index=False),  # Convert DataFrame to CSV
                    type="text/csv",
                )

                # Enable CSV download for the team stats table
                team_download_button = dcc.Download(
                    id='download-team-stats',
                    data=team_stats_df.to_csv(index=False),  # Convert DataFrame to CSV
                    type="text/csv",
                )

                # Create tabs for the tables
                tabs = dcc.Tabs([
                    dcc.Tab(
                        label='Player Statistics',
                        children=html.Div([player_download_button, player_table])
                    ),
                    dcc.Tab(
                        label='Data Quality Report',
                        children=html.Div(data_quality_table)
                    ),
                    dcc.Tab(
                        label='Team Statistics',
                        children=html.Div([team_download_button, team_stats_table])
                    )
                ])

                logger.debug("Finished data analysis process successfully")
                return tabs, dash.no_update, dash.no_update  # Update all containers

            except Exception as e:
                logger.error(f"Error in analysis: {e}", exc_info=True)
                return None, html.Div(f"Error: {str(e)}"), None
            
        logger.error(f"Unexpected trigger: {triggered_id}")
        raise PreventUpdate