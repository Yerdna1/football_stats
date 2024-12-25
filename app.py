from datetime import datetime
import os
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import logging
import requests
from api import FootballAPI
from sport_layouts import (
    create_winless_streaks_tab,
    create_team_analysis_tab,
    create_next_round_tab,
    create_league_stats_tab
)
from sport_analyzers import WinlessStreakAnalyzer, TeamAnalyzer, FixtureAnalyzer, LeagueAnalyzer
from config import ALL_LEAGUES, API_KEY, BASE_URL, LEAGUE_NAMES


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DashboardApp:
    def __init__(self, api):
        # Initialize the Dash app
        self.app = dash.Dash(__name__)
        self.server = self.app.server  # Expose the Flask server for Gunicorn
        self.api = api
        self.setup_layout()
        self.setup_callbacks()
    @staticmethod
    def get_league_display_name(league_id):
        """Get formatted league name with flag for display"""
        if league_id == ALL_LEAGUES:
            return "All Leagues"
        
        league_info = LEAGUE_NAMES.get(league_id, {})
        if league_info:
            return f"{league_info['flag']} {league_info['name']} ({league_info['country']})"
        return "Selected League"

    def setup_layout(self):
        # Define the layout of the app
        self.app.layout = html.Div([
            dcc.Tabs([  # Updated to use `dcc.Tabs` directly
                create_winless_streaks_tab(),
                create_team_analysis_tab(),
                create_next_round_tab(),
                create_league_stats_tab(),
            ])
        ])
    
    def setup_callbacks(self):
        api = self.api  # Store reference to api to use in callbacks
        
        # Callback to update the winless streaks chart and data table
        @self.app.callback(
            [Output('winless-streaks-chart', 'figure'),
             Output('last-matches-table', 'data')],
            [Input('winless-league-dropdown', 'value'),  # Changed from 'league-dropdown'
             Input('current-streak-filter', 'value')]
        )
        def update_winless_data(league_id, current_streak_filter):
            try:
                
                fixtures = api.fetch_fixtures(league_id)  # This will handle ALL_LEAGUES internally

                
               
                if not fixtures:
                    return px.bar(title="No data available"), []
                
                show_current_only = 'current' in current_streak_filter
                streaks = WinlessStreakAnalyzer.calculate_streaks(
                    fixtures, current_only=show_current_only)
                
                df = pd.DataFrame(list(streaks.items()), columns=['Team', 'Winless Streak'])
                df = df.sort_values('Winless Streak', ascending=False)
                
                # Create bar chart
                top_10_df = df.head(10)
                fig = px.bar(top_10_df, 
                             x='Team', 
                             y='Winless Streak',
                            title=f'Top Winless Streaks in {LEAGUE_NAMES.get(league_id, {}).get("name", "Selected League")}')

                
                fig.update_layout(
                    xaxis_tickangle=45,
                    margin=dict(t=50, l=50, r=50, b=100),
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    font_family="Arial, sans-serif",
                    showlegend=False
                )
                
                fig.update_traces(
                    marker_color='rgb(55, 83, 109)',
                    hovertemplate='Team: %{x}<br>Winless Streak: %{y}<extra></extra>'
                )
                
                fig.update_xaxes(
                    gridcolor='lightgrey',
                    showline=True,
                    linewidth=1,
                    linecolor='lightgrey'
                )
                
                fig.update_yaxes(
                    gridcolor='lightgrey',
                    showline=True,
                    linewidth=1,
                    linecolor='lightgrey'
                )
                
                # Create table data
                table_data = []
                for _, row in df.head(5).iterrows():
                    team = row['Team']
                    last_match = WinlessStreakAnalyzer.get_last_match(fixtures, team)
                    if last_match:
                        table_data.append({
                            'team': team,
                            'streak': int(row['Winless Streak']),
                            'result': last_match['result'],
                            'score': last_match['score'],
                            'date': last_match['date']
                        })
                
                return fig, table_data
                
            except Exception as e:
                logger.error(f"Error updating data: {str(e)}")
                return px.bar(title="Error loading data"), []

        @self.app.callback(
    [Output('team-dropdown', 'options'),
     Output('team-dropdown', 'value')],
    Input('team-league-dropdown', 'value')
        )
        def update_teams(league_id):
            if not league_id or league_id == ALL_LEAGUES:
                return [], None
            
            standings = api.fetch_standings(league_id)
            if not standings or not standings.get('response'):
                return [], None
                    
            teams = standings['response'][0]['league']['standings'][0]
            options = [{'label': team['team']['name'], 
                        'value': team['team']['id']} 
                    for team in teams]
            
            # Sort teams alphabetically by name
           #  sorted_options = sorted(options, key=lambda x: x['label'])
            
            # Reset the selected value when league changes
            return sorted(options, key=lambda x: x['label']), None

        # Callback to update team analysis results
        @self.app.callback(
            [Output('team-results-table', 'data'),
             Output('team-results-table', 'style_data_conditional'),
             Output('scoreless-teams-table', 'data')],
            [Input('team-league-dropdown', 'value'),
             Input('team-dropdown', 'value')]
        )
        def update_team_analysis(league_id, team_id):
            if not team_id:
                return [], [], []
                
            fixtures = api.fetch_fixtures(league_id, team_id=team_id)
            results = TeamAnalyzer.analyze_team_results(fixtures, team_id)
            
            # Prepare results table data
            table_data = []
            style_conditions = [{
                'if': {'column_id': 'result_display'},
                'fontWeight': 'bold'
            }]
            
            for res in results:
                result = res['result']
                table_data.append({
                    'date': res['date'],
                    'opponent': res['opponent'],
                    'score': res['score'],
                    'result_display': result['symbol']
                })
                style_conditions.append({
                    'if': {'column_id': 'result_display',
                           'filter_query': f'{{result_display}} = "{result["symbol"]}"'},
                    'color': result['color']
                })
            
            # Get scoreless teams
            scoreless = TeamAnalyzer.find_scoreless_teams(fixtures)
            
            return table_data, style_conditions, scoreless

        @self.app.callback(
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

        @self.app.callback(
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
            
        @self.app.callback(
        [Output('avg-goals-stat', 'children'),
        Output('avg-yellow-stat', 'children'),
        Output('avg-red-stat', 'children'),
        Output('common-results-table', 'data')],
        Input('stats-league-dropdown', 'value')
             )
        def update_league_stats(league_id):
            if not league_id:
                return "N/A", "N/A", "N/A", []
                
            try:
                # Handle ALL_LEAGUES case
                if league_id == ALL_LEAGUES:
                    fixtures = LeagueAnalyzer.get_all_leagues_fixtures(api)
                else:
                    fixtures = api.fetch_fixtures(league_id)

                if not fixtures:
                    return "N/A", "N/A", "N/A", []
                
                # Calculate statistics
                stats = LeagueAnalyzer.calculate_league_stats(fixtures)
                
                return (
                    f"{stats['avg_goals']:.2f}",
                    f"{stats['avg_yellows']:.2f}",
                    f"{stats['avg_reds']:.2f}",
                    stats['common_results']
                )
            except Exception as e:
                print(f"Error calculating league stats: {str(e)}")
                return "N/A", "N/A", "N/A", []   
        
         # League Goals Comparison Callback
        @self.app.callback(
            Output('league-goals-comparison', 'figure'),
            Input('stats-league-dropdown', 'value')  # We'll use this to trigger updates
        )
        def update_goals_comparison(_):
            try:
                # Get statistics for all leagues
                league_stats = []
                
                for league_id, league_info in LEAGUE_NAMES.items():
                    if isinstance(league_id, int):  # Skip ALL_LEAGUES entry
                        try:
                            fixtures = api.fetch_fixtures(league_id)
                            if fixtures:
                                total_goals = 0
                                total_matches = 0
                                
                                for fixture in fixtures:
                                    if fixture['fixture']['status']['short'] == 'FT':
                                        total_matches += 1
                                        total_goals += (fixture['score']['fulltime']['home'] + 
                                                    fixture['score']['fulltime']['away'])
                                
                                if total_matches > 0:
                                    avg_goals = round(total_goals / total_matches, 2)
                                    league_stats.append({
                                        'league': f"{league_info['flag']} {league_info['name']}",
                                        'avg_goals': avg_goals,
                                        'total_goals': total_goals,
                                        'matches': total_matches
                                    })
                        except Exception as e:
                            print(f"Error processing league {league_id}: {str(e)}")
                            continue
                
                # Sort by average goals
                league_stats = sorted(league_stats, key=lambda x: x['avg_goals'], reverse=True)
                
                # Create DataFrame for plotting
                df = pd.DataFrame(league_stats)
                
                if df.empty:
                    raise ValueError("No data available")
                
                # Create bar chart
                fig = px.bar(df, 
                            x='league', 
                            y='avg_goals',
                            title='Average Goals per Match by League',
                            labels={'league': 'League', 
                                   'avg_goals': 'Average Goals per Match'},
                            text=df['avg_goals'].round(2))  # Show values on bars
                
                # Customize layout
                fig.update_traces(
                    texttemplate='%{text}',
                    textposition='outside',
                    marker_color='rgb(55, 83, 109)'
                )
                
                fig.update_layout(
                    xaxis_tickangle=45,
                    margin=dict(t=50, l=50, r=50, b=120),  # Increased bottom margin
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    font_family="Arial, sans-serif",
                    showlegend=False,
                    height=600,  # Make chart taller to accommodate all leagues
                    yaxis_title="Average Goals per Match",
                    xaxis_title="League"
                )
                
                fig.update_xaxes(
                    gridcolor='lightgrey',
                    showline=True,
                    linewidth=1,
                    linecolor='lightgrey'
                )
                
                fig.update_yaxes(
                    gridcolor='lightgrey',
                    showline=True,
                    linewidth=1,
                    linecolor='lightgrey',
                    range=[0, max(df['avg_goals']) * 1.1]  # Add 10% padding to y-axis
                )
                
                return fig
                
            except Exception as e:
                print(f"Error creating goals comparison chart: {str(e)}")
                empty_fig = px.bar(title="No data available")
                empty_fig.update_layout(
                    xaxis_title="League",
                    yaxis_title="Average Goals per Match",
                    height=400
                )
                return empty_fig 

    def run(self, debug=True):
        # Run the Dash app
        self.app.run_server(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

if __name__ == '__main__':
    # Instantiate the API and app
    football_api = FootballAPI(API_KEY, BASE_URL)
    dashboard = DashboardApp(football_api)
    dashboard.run(debug=True)