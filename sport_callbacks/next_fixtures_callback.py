import html
from venv import logger
from dash.dependencies import Input, Output
from datetime import datetime
import plotly.express as px
import requests
from config import ALL_LEAGUES
from sport_analyzers import LeagueAnalyzer
from sport_analyzers.fixture_analyzer import FixtureAnalyzer 
 
def setup_next_fixtures_callbacks(app, api):
    @app.callback(
        [Output('next-fixtures-table', 'data'),
         Output('fixture-select-dropdown', 'options')],
        Input('next-round-league-dropdown', 'value')
    )
    def update_next_fixtures(league_id):
        if league_id == ALL_LEAGUES:
            fixtures = LeagueAnalyzer.get_all_leagues_fixtures(api)
            # Filter to get only upcoming matches
            next_fixtures = [f for f in fixtures if f['fixture']['status']['short'] == 'NS']
            # Sort by date and take more matches
            next_fixtures = sorted(next_fixtures, 
                                key=lambda x: x['fixture']['date'])[:50]  # Increased from 10 to 30
        else:
            next_fixtures = api.fetch_next_fixtures(league_id)
        
        try:
            # Group fixtures by date
            grouped_fixtures = {}
            table_data = []
            dropdown_options = []
            
            for fixture in next_fixtures:
                # Parse date
                fixture_date = datetime.strptime(fixture['fixture']['date'], 
                                               '%Y-%m-%dT%H:%M:%S%z')
                date_key = fixture_date.strftime('%Y-%m-%d')
                
                fixture_data = {
                    'date': date_key,
                    'time': fixture_date.strftime('%H:%M'),
                    'home_team': fixture['teams']['home']['name'],
                    'away_team': fixture['teams']['away']['name'],
                    'venue': fixture['fixture']['venue']['name'],
                    'fixture_id': fixture['fixture']['id'],
                    'league': fixture['league']['name'],
                    'round': fixture['league']['round'],
                    # Add date header for grouping
                    'date_header': fixture_date.strftime('%A, %B %d, %Y')
                }
                
                # Fetch and add odds
                odds = api.fetch_match_odds(fixture['fixture']['id'])
                if odds:
                    fixture_data.update({
                        'home_odds': format_odds(odds.get('home')),
                        'draw_odds': format_odds(odds.get('draw')),
                        'away_odds': format_odds(odds.get('away'))
                    })
                else:
                    fixture_data.update({
                        'home_odds': 'N/A',
                        'draw_odds': 'N/A',
                        'away_odds': 'N/A'
                    })
                
                # Group by date
                if date_key not in grouped_fixtures:
                    grouped_fixtures[date_key] = []
                grouped_fixtures[date_key].append(fixture_data)
                
                # Add to dropdown options
                dropdown_options.append({
                    'label': f"{fixture_data['date']} {fixture_data['time']} - {fixture_data['home_team']} vs {fixture_data['away_team']}",
                    'value': fixture['fixture']['id']
                })
            
            # Sort dates and create final table data
            for date_key in sorted(grouped_fixtures.keys()):
                # Sort fixtures within each date by time
                day_fixtures = sorted(grouped_fixtures[date_key], 
                                   key=lambda x: x['time'])
                
                # Add a date header row
                if day_fixtures:
                    table_data.append({
                        'date': day_fixtures[0]['date_header'],
                        'time': '',
                        'home_team': '',
                        'away_team': '',
                        'venue': '',
                        'league': '',
                        'round': '',
                        'home_odds': '',
                        'draw_odds': '',
                        'away_odds': '',
                        'is_header': True
                    })
                    table_data.extend(day_fixtures)
            
            return table_data, dropdown_options
            
        except Exception as e:
            logger.error(f"Error fetching next fixtures: {str(e)}")
            return [], []

    def format_odds(odds_value):
        try:
            return f"{float(odds_value):.2f}"
        except (ValueError, TypeError):
            return "N/A"