import logging
from typing import Dict
from venv import logger
from dash.dependencies import Input, Output
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

def setup_firebase_analysis_callbacks(app, db):
    @app.callback(
    Output("selected-data-source", "data"),
    Input("data-source-switch", "value"),
    )
    def update_data_source(data_source):
        return data_source  # Update store with the selected value
    
    @app.callback(
        Output('player-stats-container', 'children'),
        [Input('analyze-data-button', 'n_clicks'),
         Input("selected-data-source", "data"),
         Input('detailed-fixture-id', 'value')]  # Added input for fixture ID
    )
    def update_analysis(n_clicks, data_source):
        if not n_clicks:
            raise PreventUpdate

        try:
            
            if data_source == "db":
                quality_stats = analyze_data_quality(db)
                fixtures = db.collection('fixtures').stream()
                fixtures_data = [fixture.to_dict() for fixture in fixtures]
            else:
                # API Call logic
                quality_stats = []  # Replace with actual API call for quality stats
                fixtures_data =[]


           
            quality_report = create_data_quality_report(quality_stats)
            player_stats = create_player_statistics(fixtures_data)
            player_df = create_player_statistics_table(player_stats)  # Create DataFrame

            # Enable CSV download for the player stats table
            download_button = dcc.Download(
                id='download-player-stats',
                filename="player_stats.csv",
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
            )

            return quality_report, html.Div([download_button, player_table])  # Return both

        except Exception as e:
            print(f"Error in analysis: {e}")
            return html.Div(f"Error: {str(e)}"), html.Div("Error loading player stats")