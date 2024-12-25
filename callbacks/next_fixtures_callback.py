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
                # Sort by date and take the nearest matches
                next_fixtures = sorted(next_fixtures, 
                                    key=lambda x: x['fixture']['date'])[:10]
            else:
                next_fixtures = api.fetch_next_fixtures(league_id)
            
            try:
                
                
                # Prepare table data
                table_data = []
                dropdown_options = []
                
                for fixture in next_fixtures:
                    fixture_data = {
                        'date': datetime.strptime(fixture['fixture']['date'], 
                                                '%Y-%m-%dT%H:%M:%S%z').strftime('%Y-%m-%d'),
                        'time': datetime.strptime(fixture['fixture']['date'], 
                                                '%Y-%m-%dT%H:%M:%S%z').strftime('%H:%M'),
                        'home_team': fixture['teams']['home']['name'],
                        'away_team': fixture['teams']['away']['name'],
                        'venue': fixture['fixture']['venue']['name'],
                        'fixture_id': fixture['fixture']['id']
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
                    table_data.append(fixture_data)
                    
                    dropdown_options.append({
                        'label': f"{fixture_data['home_team']} vs {fixture_data['away_team']}",
                        'value': fixture['fixture']['id']
                    })
                
                return table_data, dropdown_options
                
            except Exception as e:
                logger.error(f"Error fetching next fixtures: {str(e)}")
                return [], []
    def format_odds(odds_value):
            try:
                return f"{float(odds_value):.2f}"
            except (ValueError, TypeError):
                return "N/A"
    @app.callback(
        [Output('home-team-stats', 'data'),
         Output('away-team-stats', 'data'),
         Output('home-team-name', 'children'),
         Output('away-team-name', 'children'),
         Output('match-analysis', 'children')],
        Input('fixture-select-dropdown', 'value')
    )
    def update_fixture_analysis(fixture_id):
            if not fixture_id:
                return [], [], "", "", ""
                
            try:
                # Modified this line to use the correct parameter
                url = f"{api.base_url}/fixtures"
                params = {'id': fixture_id}
                response = requests.get(url, headers=api.headers, params=params)
                fixtures = response.json().get('response', []) if response.status_code == 200 else []
                
                if not fixtures:
                    return [], [], "", "", "No fixture data available"
                    
                fixture = fixtures[0]
                league_id = fixture['league']['id']
                home_team_id = fixture['teams']['home']['id']
                away_team_id = fixture['teams']['away']['id']
                
                # Fetch statistics
                home_players = api.fetch_player_statistics(league_id, home_team_id)
                away_players = api.fetch_player_statistics(league_id, away_team_id)
                home_team_stats = api.fetch_team_statistics(league_id, home_team_id)
                away_team_stats = api.fetch_team_statistics(league_id, away_team_id)
                
                # Analyze match
                analysis = FixtureAnalyzer.analyze_match_statistics(
                    fixture,
                    home_players + away_players,
                    {home_team_id: home_team_stats, away_team_id: away_team_stats}
                )
                
                # Prepare player statistics tables
                def prepare_player_stats(players):
                    return [{
                        'name': p['name'],
                        'goals': p['goals'],
                        'assists': p['assists'],
                        'yellow_cards': p['yellow_cards'],
                        'red_cards': p['red_cards'],
                        'minutes': p['minutes'],
                        'matches': p['matches'],
                        'status': 'Injured' if p['injured'] else 'OK',
                        'position': p['position']
                    } for p in players]
                
                home_stats = prepare_player_stats(analysis['home_team']['players'])
                away_stats = prepare_player_stats(analysis['away_team']['players'])
                
                # Prepare analysis points
                analysis_points = html.Ul([
                    html.Li(point) for point in analysis['key_points']
                ])
                
                return (
                    home_stats,
                    away_stats,
                    analysis['home_team']['name'],
                    analysis['away_team']['name'],
                    analysis_points
                )
                
            except Exception as e:
                logger.error(f"Error analyzing fixture: {str(e)}")
                return [], [], "", "", "Error analyzing fixture"
            