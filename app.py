from collections import defaultdict
import json
import os
import dash
from dash import dcc, html
import logging
from api import FootballAPI
from league_names import LEAGUE_NAMES
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
from config import ALL_LEAGUES, API_KEY, BASE_URL, FootballDataFetcher, generate_league_names_dict
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
        setup_team_analysis_callbacks(self.app, self.api, db)
        setup_next_fixtures_callbacks(self.app, self.api)
        setup_league_stats_callbacks(self.app, self.api)  
        setup_form_analysis_callbacks(self.app, self.api)
        add_stats_callback(self.app, self.api)
        setup_data_collection_callbacks(self.app, self.api)
        setup_firebase_analysis_callbacks(self.app,db)
    
    
    def run(self, debug=True):
        # Run the Dash app
        self.app.run_server(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
    
    
    """  fetcher = FootballDataFetcher()
        active_leagues = fetcher.find_active_leagues()
        
        print(f"\nSummary of Active Leagues for 2024 Season:")
        print("=========================================")
        
        # Group leagues by country
        leagues_by_country = defaultdict(list)
        for league in active_leagues:
            leagues_by_country[league['country']].append(league)
        
        # Print summary
        total_countries = len(leagues_by_country)
        total_leagues = len(active_leagues)
        print(f"\nFound {total_leagues} active leagues across {total_countries} countries:\n")
        
        for country, leagues in sorted(leagues_by_country.items()):
            flag = leagues[0]['flag']
            print(f"{flag} {country}:")
            for league in leagues:
                print(f"  • {league['name']} ({league['type']}) - {league['fixture_count']} fixtures")
        
        # Generate the LEAGUE_NAMES dictionary
        league_names_content = generate_league_names_dict(active_leagues)
        
        # Get current directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Save to Python file
        python_file_path = os.path.join(current_dir, 'league_names.py')
        print(f"\nSaving Python dictionary to: {python_file_path}")
        try:
            with open(python_file_path, 'w', encoding='utf-8') as f:
                f.write("# Auto-generated league names dictionary for 2024 season\n")
                f.write("ALL_LEAGUES = -1  # Special value for all leagues\n\n")
                f.write(league_names_content)
            print("✅ Successfully saved Python dictionary")
        except Exception as e:
            print(f"❌ Error saving Python file: {e}")
        
        # Save JSON version
        json_file_path = os.path.join(current_dir, 'league_names.json')
        print(f"\nSaving JSON file to: {json_file_path}")
        try:
            # Create JSON dictionary
            league_names_dict = {
                -1: {"name": "All Leagues", "flag": "🌍", "country": "Global"}
            }
            for league in active_leagues:
                if league['type'].lower() == 'league':
                    league_names_dict[league['id']] = {
                        "name": league['name'],
                        "flag": league['flag'],
                        "country": league['country']
                    }
            
            with open(json_file_path, 'w', encoding='utf-8') as f:
                json.dump(league_names_dict, f, indent=4, ensure_ascii=False)
            print("✅ Successfully saved JSON file")
        except Exception as e:
            print(f"❌ Error saving JSON file: {e}")
        
        # Print the dictionary content to console as well
        print("\nGenerated LEAGUE_NAMES dictionary:")
        print("=================================")
        print(league_names_content) """



football_api = FootballAPI(API_KEY, BASE_URL)
dashboard = DashboardApp(football_api)
app = dashboard.server  # This is what gunicorn will use

if __name__ == '__main__':
    if os.environ.get('RENDER'):
        dashboard.run(debug=False)
    else:
        dashboard.run(debug=True)

  
