import os
import dash
from dash import dcc, html
import logging
from api import FootballAPI
from sport_callbacks import (
    setup_winless_streaks_callbacks,
    setup_team_analysis_callbacks,
    setup_next_fixtures_callbacks,
    setup_league_stats_callbacks,
    setup_form_analysis_callbacks,
    setup_usage_api_callbacks
    )
from sport_layouts import (
    create_winless_streaks_tab,
    create_team_analysis_tab,
    create_next_round_tab,
    create_league_stats_tab,
    create_form_analysis_tab
)
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
        self.app.layout = html.Div([
            dcc.Tabs([
                create_winless_streaks_tab(),
                create_team_analysis_tab(),
                create_next_round_tab(),
                create_league_stats_tab(),
                create_form_analysis_tab()
            ]),
            # API Usage display at bottom
            html.Div([
                html.Span("API Usage: ", style={'fontWeight': 'bold'}),
                html.Span(id='api-usage-display'),
                dcc.Interval(
                    id='interval-component',
                    interval=30*1000,
                    n_intervals=0
                )
            ], style={
                'position': 'fixed',
                'bottom': '10px',
                'right': '10px',
                'padding': '5px 10px',
                'backgroundColor': '#f8f9fa',
                'borderRadius': '5px',
                'boxShadow': '0 -2px 5px rgba(0,0,0,0.1)',
                'zIndex': '1000'
            })
        ])
        
    def setup_callbacks(self):
        api = self.api
        setup_winless_streaks_callbacks(self.app, self.api)
        setup_team_analysis_callbacks(self.app, self.api)
        setup_next_fixtures_callbacks(self.app, self.api)
        setup_league_stats_callbacks(self.app, self.api)  # Corrected: no comma
        setup_form_analysis_callbacks(self.app, self.api)
        setup_usage_api_callbacks(self.app,self.api)
    
    def run(self, debug=True):
        # Run the Dash app
        self.app.run_server(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

if __name__ == '__main__':
    # Instantiate the API and app
    football_api = FootballAPI(API_KEY, BASE_URL)
    dashboard = DashboardApp(football_api)
    dashboard.run(debug=True)
