import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import logging
from api import FootballAPI
from analyzers import WinlessStreakAnalyzer, TeamAnalyzer
from layouts import create_winless_streaks_tab, create_team_analysis_tab
from config import API_KEY, BASE_URL, LEAGUE_NAMES

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

    def setup_layout(self):
        # Define the layout of the app
        self.app.layout = html.Div([
            dcc.Tabs([  # Updated to use `dcc.Tabs` directly
                create_winless_streaks_tab(),
                create_team_analysis_tab()
            ])
        ])

    def setup_callbacks(self):
        # Callback to update the winless streaks chart and data table
        @self.app.callback(
            [Output('winless-streaks-chart', 'figure'),
             Output('last-matches-table', 'data')],
            [Input('league-dropdown', 'value'),
             Input('current-streak-filter', 'value')]
        )
        def update_winless_data(league_id, current_streak_filter):
            try:
                fixtures = self.api.fetch_fixtures(league_id)
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
                             title=f'Top Winless Streaks in {LEAGUE_NAMES.get(league_id, "Selected League")}')
                
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

        # Callback to update the teams dropdown based on selected league
        @self.app.callback(
            Output('team-dropdown', 'options'),
            Input('team-league-dropdown', 'value')
        )
        def update_teams(league_id):
            teams = self.api.fetch_teams(league_id)
            return [{'label': team['team']['name'], 
                     'value': team['team']['id']} 
                    for team in teams]

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
                
            fixtures = self.api.fetch_fixtures(league_id, team_id=team_id)
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

    def run(self, debug=True):
        # Run the Dash app
        self.app.run_server(debug=debug)

if __name__ == '__main__':
    # Instantiate the API and app
    football_api = FootballAPI(API_KEY, BASE_URL)
    dashboard = DashboardApp(football_api)
    dashboard.run(debug=True)
