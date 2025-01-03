import logging
from collections import defaultdict
import pandas as pd
import plotly.express as px
from dash import html, dash_table, dcc
import time
from google.api_core.exceptions import ServiceUnavailable
from typing import Dict, Any

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)






def analyze_data_quality(fixtures_data):
    """Analyze fixtures data quality from Firebase"""
    logger.info("Starting analyze_data_quality function")
    try:

     
        
        logger.info(f"Total fixtures loaded: {len(fixtures_data)}")  # Debug print
        
        # Basic Counts
        stats = {
            'total_fixtures': len(fixtures_data),
            'leagues': defaultdict(lambda: {
                'fixtures_count': 0,
                'seasons': set(),
                'teams': set(),
                'players': set(),
                'complete_data': 0,
                'missing_data': 0,
                'name': '' # Add name
            })
        }
        
        # Analyze each fixture
        for fixture in fixtures_data:
            try:
                logger.info(f"Processing fixture: {fixture.get('id')}")
                league_data = fixture.get('league', {})
                league_id = str(league_data.get('id', ''))  # Convert to string
                league_name = league_data.get('name', 'Unknown')  # Default to 'Unknown'
                season = str(league_data.get('season', ''))  # Convert to string
                
                # Skip if no league ID
                if not league_id:
                    logger.warning(f"Skipping fixture with no league ID: {fixture.get('id')}")
                    continue
                
                logger.info(f"Processing fixture for league: {league_name}, season: {season}")
                
                # Update league stats
                stats['leagues'][league_id]['fixtures_count'] += 1
                stats['leagues'][league_id]['seasons'].add(season)
                stats['leagues'][league_id]['name'] = league_name
                
                # Check teams
                teams_data = fixture.get('teams', {})
                home_team = teams_data.get('home', {}).get('id')
                away_team = teams_data.get('away', {}).get('id')
                if home_team:
                    stats['leagues'][league_id]['teams'].add(str(home_team)) # Convert to string
                if away_team:
                    stats['leagues'][league_id]['teams'].add(str(away_team)) # Convert to string
                
                # Check data completeness
                if check_fixture_completeness(fixture):
                    stats['leagues'][league_id]['complete_data'] += 1
                else:
                    stats['leagues'][league_id]['missing_data'] += 1
                
                # Collect players
                players_data = fixture.get('players', [])
                for team_data in players_data:
                    for player in team_data.get('players', []):
                        player_id = str(player.get('player', {}).get('id', ''))
                        if player_id:
                            stats['leagues'][league_id]['players'].add(player_id) # Convert to string
            
            except Exception as e:
                logger.error(f"Error processing fixture: {e}, fixture: {fixture.get('id')}")
                continue
        
        logger.info(f"Finished analyze_data_quality, stats: {stats}")
        return stats
    
    except Exception as e:
        logger.error(f"Error analyzing data: {e}", exc_info=True)
        return None

def check_fixture_completeness(fixture):
    logger.info(f"Starting check_fixture_completeness for fixture: {fixture.get('id')}")
    required_fields = [
        ('events', []),
        ('lineups', []),
        ('statistics', []),
        ('players', [])
    ]
    
    for field, default in required_fields:
         if field not in fixture or fixture[field] == default:
            logger.info(f"Missing or empty field: {field} for fixture: {fixture.get('id')}")
            return False
    logger.info(f"Fixture {fixture.get('id')} is complete")
    return True

def create_data_quality_report(stats, output_csv_path='data_quality_report.csv'):
    """Create a report of data quality and export it to a CSV file."""
    logger.info("Starting create_data_quality_report function")
    
    if not stats:
        logger.info("No stats available, returning 'No data available'")
        return "No data available"
    
    league_rows = []
    for league_id, league_data in stats['leagues'].items():
        fixtures_count = league_data['fixtures_count']
        logger.info(f"Processing league: {league_data.get('name')}, with {fixtures_count} fixtures")
        
        # Calculate data quality percentage
        if fixtures_count > 0:  # Avoid division by zero
            data_quality_percentage = (league_data['complete_data'] / fixtures_count * 100)
        else:
            data_quality_percentage = 0
        
        # Additional data quality checks
        missing_statistics = fixtures_count - league_data.get('statistics_count', 0)
        missing_lineups = fixtures_count - league_data.get('lineups_count', 0)
        missing_players = fixtures_count - league_data.get('players_count', 0)
        
        league_rows.append({
            'League': league_data.get('name', 'Unknown'),
            'Total Fixtures': fixtures_count,
            'Seasons': len(league_data.get('seasons', [])),
            'Teams': len(league_data.get('teams', [])),
            'Players': len(league_data.get('players', [])),
            'Complete Data': league_data.get('complete_data', 0),
            'Missing Data': league_data.get('missing_data', 0),
            'Data Quality %': f"{data_quality_percentage:.1f}%",
            'Missing Statistics': missing_statistics,
            'Missing Lineups': missing_lineups,
            'Missing Players': missing_players
        })
    
    # Create a DataFrame from the league_rows
    df = pd.DataFrame(league_rows)
    
    # Export the DataFrame to a CSV file
    df.to_csv(output_csv_path, index=False)
    logger.info(f"Data quality report exported to {output_csv_path}")
    
    # Generate the HTML report
    report = html.Div([
        # Overall Summary
        html.Div([
            html.H3("Data Quality Overview", className='text-xl font-bold mb-4'),
            html.P(f"Total Fixtures in Database: {stats['total_fixtures']}", className='mb-2'),
            html.P(f"Total Leagues: {len(stats['leagues'])}", className='mb-4'),
        ]),
        
        # League-wise Summary
        html.Div([
            html.H3("League-wise Data Quality", className='text-xl font-bold mb-4'),
            dash_table.DataTable(
                id='data-quality-table',
                columns=[{'name': col, 'id': col} for col in [
                    'League', 'Total Fixtures', 'Seasons', 'Teams', 
                    'Players', 'Complete Data', 'Missing Data', 'Data Quality %',
                    'Missing Statistics', 'Missing Lineups', 'Missing Players'
                ]],
                data=league_rows,
                filter_action='native',  # Enable filtering
                sort_action='native',    # Enable sorting
                sort_mode='multi',       # Allow multi-column sorting
                page_action='native',    # Enable pagination
                page_size=20,            # Set page size
                style_table={'overflowX': 'auto'},
                style_cell={'textAlign': 'left', 'padding': '10px'},
                style_header={
                    'backgroundColor': 'rgb(230, 230, 230)',
                    'fontWeight': 'bold'
                },
            )
        ], className='mb-8'),
    ])
    
    logger.info("Finished create_data_quality_report function")
    return report, df

def create_player_statistics(fixtures_data):
    """Analyze player statistics from fixtures"""
   
    player_stats = defaultdict(lambda: {
        'name': '',
        'team': '',
        'appearances': 0,
        'minutes': 0,
        'goals': 0,
        'assists': 0,
        'yellow_cards': 0,
        'red_cards': 0,
        'rating': [],
        'shots_total': 0,
        'shots_on': 0,
        'passes_total': 0,
        'passes_accuracy': [],
        'tackles': 0,
        'interceptions': 0,
        'duels_total': 0,
        'duels_won': 0
    })
    
    for fixture in fixtures_data:
        try:
        
            for team_data in fixture.get('players', []):
                for player_data in team_data.get('players', []):
                    player = player_data['player']
                    stats = player_data['statistics'][0]
                    player_id = str(player['id'])
   
                    
                    # Basic info
                    player_stats[player_id]['name'] = player['name']
                    player_stats[player_id]['team'] = team_data['team']['name']
                    
                    # Game stats
                    if stats['games'].get('minutes'):
                        player_stats[player_id]['appearances'] += 1
                        player_stats[player_id]['minutes'] += stats['games'].get('minutes')
                
                    
                    if stats['games'].get('rating'):
                         player_stats[player_id]['rating'].append(float(stats['games'].get('rating')))
              
                    
                    # Goals and assists
                    if stats.get('goals'):
                        player_stats[player_id]['goals'] += stats['goals'].get('total', 0) or 0
                        player_stats[player_id]['assists'] += stats['goals'].get('assists', 0) or 0
       
                    # Cards
                    if stats.get('cards'):
                        player_stats[player_id]['yellow_cards'] += stats['cards'].get('yellow', 0) or 0
                        player_stats[player_id]['red_cards'] += stats['cards'].get('red', 0) or 0
  
                    # Shots
                    if stats.get('shots'):
                        player_stats[player_id]['shots_total'] += stats['shots'].get('total', 0) or 0
                        player_stats[player_id]['shots_on'] += stats['shots'].get('on', 0) or 0
            
                    
                    # Passes
                    if stats.get('passes'):
                        player_stats[player_id]['passes_total'] += stats['passes'].get('total', 0) or 0
                        if stats['passes'].get('accuracy'):
                            player_stats[player_id]['passes_accuracy'].append(float(stats['passes'].get('accuracy')))
        
                    
                    # Tackles and interceptions
                    if stats.get('tackles'):
                        player_stats[player_id]['tackles'] += stats['tackles'].get('total', 0) or 0
                        player_stats[player_id]['interceptions'] += stats['tackles'].get('interceptions', 0) or 0
            

                    
                    # Duels
                    if stats.get('duels'):
                        player_stats[player_id]['duels_total'] += stats['duels'].get('total', 0) or 0
                        player_stats[player_id]['duels_won'] += stats['duels'].get('won', 0) or 0
            
        except Exception as e:
            logger.error(f"Error processing player statistics: {e}, fixture id: {fixture.get('id')}", exc_info=True)
            continue
    
    logger.info("Finished create_player_statistics function")
    return player_stats

def create_player_statistics_table(player_stats: Dict[str, Dict[str, Any]]) -> pd.DataFrame:
    """
    Create a Pandas DataFrame with player statistics and export it to a CSV file.

    Args:
        player_stats: A dictionary containing player statistics.

    Returns:
        A Pandas DataFrame with player statistics.
    """
    logger.info("Starting create_player_statistics_table function")
    rows = []
    for player_id, stats in player_stats.items():
        if stats['appearances'] > 0:  # Only show players who played
            avg_rating = sum(stats['rating']) / len(stats['rating']) if stats['rating'] else 0
            pass_accuracy = sum(stats['passes_accuracy']) / len(stats['passes_accuracy']) if stats['passes_accuracy'] else 0

            rows.append({
                'Name': stats['name'],
                'Team': stats['team'],
                'Apps': stats['appearances'],
                'Minutes': stats['minutes'],
                'Goals': stats['goals'],
                'Assists': stats['assists'],
                'Rating': avg_rating,  # Store as numeric for sorting/calculations
                'Yellow Cards': stats['yellow_cards'],
                'Red Cards': stats['red_cards'],
                'Shots': stats['shots_total'],
                'Shots on Target': stats['shots_on'],
                'Passes': stats['passes_total'],
                'Pass Accuracy': pass_accuracy,  # Store as numeric for sorting/calculations
                'Tackles': stats['tackles'],
                'Interceptions': stats['interceptions'],
                'Duels Won': (stats['duels_won'] / stats['duels_total'] * 100) if stats['duels_total'] > 0 else 0  # Store as numeric
            })
            logger.info(f"Finished processing player: {stats['name']}, id: {player_id}")

    df = pd.DataFrame(rows)
    logger.info("Finished creating dataframe")

    # Format columns for display *after* DataFrame creation
    df['Rating'] = df['Rating'].apply(lambda x: f"{x:.2f}")
    df['Pass Accuracy'] = df['Pass Accuracy'].apply(lambda x: f"{x:.1f}%")
    df['Duels Won'] = df['Duels Won'].apply(lambda x: f"{x:.1f}%")
    logger.info("Finished formatting the dataframe")

    # Export DataFrame to CSV
    csv_filename = "player_statistics.csv"
    df.to_csv(csv_filename, index=False)
    logger.info(f"Exported player statistics to {csv_filename}")

    logger.info("Finished create_player_statistics_table function")
    return df  # Return the Pandas DataFrame