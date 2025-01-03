from venv import logger

import pandas as pd
import logging
from collections import defaultdict
import pandas as pd
import plotly.express as px
from dash import html, dash_table, dcc
import time
from google.api_core.exceptions import ServiceUnavailable
from typing import Dict, Any


def create_team_report(team_stats, team_quality):
    """Create a report summarizing team statistics and data quality"""
    logger.info("Starting create_team_report function")
    
    rows = []
    for team_id, stats in team_stats.items():
        quality = team_quality.get(team_id, {})
        matches_played = stats['matches_played']
        
        # Calculate averages
        avg_possession = sum(stats['avg_possession']) / len(stats['avg_possession']) if stats['avg_possession'] else 0
        avg_shots = sum(stats['avg_shots']) / len(stats['avg_shots']) if stats['avg_shots'] else 0
        avg_passes = sum(stats['avg_passes']) / len(stats['avg_passes']) if stats['avg_passes'] else 0
        avg_tackles = sum(stats['avg_tackles']) / len(stats['avg_tackles']) if stats['avg_tackles'] else 0
        avg_interceptions = sum(stats['avg_interceptions']) / len(stats['avg_interceptions']) if stats['avg_interceptions'] else 0
        
        rows.append({
            'Team': stats['name'],
            'League': stats['league'],
            'Matches Played': matches_played,
            'Wins': stats['wins'],
            'Draws': stats['draws'],
            'Losses': stats['losses'],
            'Goals Scored': stats['goals_scored'],
            'Goals Conceded': stats['goals_conceded'],
            'Clean Sheets': stats['clean_sheets'],
            'Failed to Score': stats['failed_to_score'],
            'Yellow Cards': stats['yellow_cards'],
            'Red Cards': stats['red_cards'],
            'Avg Possession': f"{avg_possession:.1f}%",
            'Avg Shots': f"{avg_shots:.1f}",
            'Avg Passes': f"{avg_passes:.1f}",
            'Avg Tackles': f"{avg_tackles:.1f}",
            'Avg Interceptions': f"{avg_interceptions:.1f}",
            'Data Quality %': f"{(quality.get('complete_data', 0) / matches_played * 100):.1f}%" if matches_played > 0 else "0%",
            'Missing Statistics': quality.get('missing_statistics', 0),
            'Missing Lineups': quality.get('missing_lineups', 0),
            'Missing Players': quality.get('missing_players', 0),
        })
    
    # Create a DataFrame
    df = pd.DataFrame(rows)
    
    # Export to CSV
    csv_filename = "team_report.csv"
    df.to_csv(csv_filename, index=False)
    logger.info(f"Exported team report to {csv_filename}")
    
    # Generate HTML report
    report = html.Div([
        html.H3("Team Report", className='text-xl font-bold mb-4'),
        dash_table.DataTable(
            id='team-report-table',
            columns=[{'name': col, 'id': col} for col in df.columns],
            data=df.to_dict('records'),
            filter_action='native',
            sort_action='native',
            page_action='native',
            page_size=20,
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'left', 'padding': '10px'},
            style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'},
        )
    ])
    
    logger.info("Finished create_team_report function")
    return report, df