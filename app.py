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
    setup_firebase_analysis_callbacks
   
    )

from sport_callbacks.fixtures_tab_data_collection_callback import setup_data_collection_callbacks
from sport_callbacks.team_analysis_callback import add_stats_callback
from sport_layouts import (
    create_winless_streaks_tab,
    create_team_analysis_tab,
    create_next_round_tab,
    create_league_stats_tab,
    create_form_analysis_tab,
    create_firebase_analysis_tab,
)
from config import ALL_LEAGUES, API_KEY, BASE_URL, LEAGUE_NAMES
from sport_layouts.fixtures_tab_firestore import create_data_collection_tab
from firebase_config import initialize_firebase

# Initialize Firebase at app startup
db = initialize_firebase()
if not db:
    raise Exception("Failed to initialize Firebase")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DashboardApp:
    def __init__(self, api):
        # Initialize the Dash app
        self.app = dash.Dash(__name__, external_stylesheets=[
        'https://codepen.io/chriddyp/pen/bWLwgP.css'
        ])
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
                create_form_analysis_tab(),
                create_data_collection_tab(),
                create_firebase_analysis_tab(),
            ]),
         
        ])
        
    def setup_callbacks(self):
        api = self.api
        setup_winless_streaks_callbacks(self.app, self.api)
        setup_team_analysis_callbacks(self.app, self.api)
        setup_next_fixtures_callbacks(self.app, self.api)
        setup_league_stats_callbacks(self.app, self.api)  
        setup_form_analysis_callbacks(self.app, self.api)
        add_stats_callback(self.app, self.api)
        setup_data_collection_callbacks(self.app, self.api)
        setup_firebase_analysis_callbacks(self.app,db)
    
    
    def run(self, debug=True):
        # Run the Dash app
        self.app.run_server(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
    
    
# Create the dashboard app
football_api = FootballAPI(API_KEY, BASE_URL)
dashboard = DashboardApp(football_api)
app = dashboard.server  # This is what gunicorn will use

if __name__ == '__main__':
    if os.environ.get('RENDER'):
        dashboard.run(debug=False)
    else:
        dashboard.run(debug=True)
