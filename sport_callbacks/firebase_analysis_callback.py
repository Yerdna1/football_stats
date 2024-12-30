from dash.dependencies import Input, Output
from datetime import datetime
import pandas as pd
import plotly.express as px
from config import ALL_LEAGUES, LEAGUE_NAMES
from sport_analyzers import LeagueAnalyzer
from dash import html, dcc, ctx
from dash.exceptions import PreventUpdate  # Import PreventUpdate
from sport_analyzers.firebase_analyzer import analyze_data_quality, create_data_quality_report, create_player_statistics, create_player_statistics_table



def setup_firebase_analysis_callbacks(app, db):
    @app.callback(
        [Output('data-quality-container', 'children'),
         Output('player-stats-container', 'children')],
        Input('analyze-data-button', 'n_clicks'),
        prevent_initial_call=True
    )
    def update_analysis(n_clicks):
        if not n_clicks:
            raise PreventUpdate
        
        try:
            # Get quality stats
            quality_stats = analyze_data_quality(db)
            quality_report = create_data_quality_report(quality_stats)
            
            # Get player stats
            fixtures = db.collection('fixtures').stream()
            fixtures_data = [fixture.to_dict() for fixture in fixtures]
            player_stats = create_player_statistics(fixtures_data)
            player_table = create_player_statistics_table(player_stats)
            
            return quality_report, player_table
            
        except Exception as e:
            print(f"Error in analysis: {e}")
            return html.Div(f"Error: {str(e)}"), html.Div("Error loading player stats")