from dash import html, dcc, ctx
from dash.dependencies import Input, Output, State
import json
from datetime import datetime
import firebase_admin
from firebase_admin import firestore
from dash.exceptions import PreventUpdate
import requests
import time
from typing import Dict, List, Any
import logging
import threading

from config import CALLS_PER_MINUTE

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GlobalState:
    def __init__(self):
        self.current_status = "Ready"
        self.current_progress = ""
        self.current_error = ""
        self.log_messages = []
        self.is_running = False

global_state = GlobalState()

class RateLimiter:
    def __init__(self, calls_per_minute=30):
        self.calls_per_minute = calls_per_minute
        self.calls = []
        self.min_interval = 60.0 /calls_per_minute

    def wait_if_needed(self):
        now = time.time()
        self.calls = [call_time for call_time in self.calls if now - call_time < 60]
        if len(self.calls) >= self.calls_per_minute:
            sleep_time = 60 - (now - self.calls[0])
            if sleep_time > 0:
                time.sleep(sleep_time)
        self.calls.append(now)

def make_api_request(url: str, headers: Dict, params: Dict = None, rate_limiter: RateLimiter = None) -> Dict:
    try:
        if rate_limiter:
            rate_limiter.wait_if_needed()
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        if data.get('errors'):
            raise Exception(f"API Error: {data['errors']}")
        return data
    except Exception as e:
        logger.error(f"API Request failed: {str(e)}")
        raise



def collect_fixture_details(fixture_id: int, api, db, rate_limiter: RateLimiter) -> Dict:
    try:
        # Check if the fixture already exists in the database
        fixture_ref = db.collection('fixtures').document(str(fixture_id))
        fixture_doc = fixture_ref.get()
        
        if fixture_doc.exists:
            logger.info(f"Fixture {fixture_id} already exists in the database. Skipping API call.")
            return fixture_doc.to_dict()
        
        # Get fixture details
        fixture_data = make_api_request(
            f"{api.base_url}/fixtures",
            headers=api.headers,
            params={'ids': fixture_id},
            rate_limiter=rate_limiter
        )
        
        if fixture_data.get('response'):
            fixture_details = fixture_data['response'][0]
            return {
                'events': fixture_details.get('events', []),
                'lineups': fixture_details.get('lineups', []),
                'statistics': fixture_details.get('statistics', []),
                'players': fixture_details.get('players', [])
            }
        else:
            logger.warning(f"No data found for fixture {fixture_id}")
            return {}
    except Exception as e:
        logger.error(f"Error collecting details for fixture {fixture_id}: {e}")
        return {}

def process_collection(api, league_id, season):
    try:

        rate_limiter = RateLimiter(30)
        
        def add_log(message):
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] {message}")
            global_state.log_messages.append(
                html.Div(f"[{timestamp}] {message}", style={'marginBottom': '5px'})
            )
            global_state.current_status = message

        add_log(f"Starting data collection for League ID: {league_id}, Season: {season}")
        
        data = make_api_request(
            f"{api.base_url}/fixtures",
            headers=api.headers,
            params={
                'league': league_id,
                'season': season,
                'status': 'FT-AET-PEN-1H-HT-2H-ET-BT-P'
            },
            rate_limiter=rate_limiter
        )
        
        if not data.get('response'):
            add_log("No fixtures found")
            global_state.is_running = False
            return
            
        fixtures = data['response']
        total_fixtures = len(fixtures)
        add_log(f"Found {total_fixtures} fixtures to process")
        
        db = firestore.client()
        add_log("Connected to Firebase database")
        
        chunk_size = 20
        chunks = [fixtures[i:i + chunk_size] for i in range(0, len(fixtures), chunk_size)]
        total_processed = 0

        for i, chunk in enumerate(chunks):
            add_log(f"\nProcessing chunk {i+1} of {len(chunks)}")
            batch = db.batch()
            
            for fixture in chunk:
                fixture_id = fixture['fixture']['id']
                fixture_id = fixture_id if isinstance(fixture_id, str) else fixture_id

                home_team = fixture['teams']['home']['name']
                away_team = fixture['teams']['away']['name']
                
                add_log(f"Processing fixture {fixture_id}: {home_team} vs {away_team}")
                details = collect_fixture_details(fixture_id, api, db, rate_limiter)
                
                fixture_data = {
                    'fixture': fixture['fixture'],
                    'league': fixture['league'],
                    'teams': fixture['teams'],
                    'goals': fixture['goals'],
                    'score': fixture['score'],
                    'events': details.get('events', []),
                    'lineups': details.get('lineups', []),
                    'statistics': details.get('statistics', []),
                    'players': details.get('players', []),
                    'updated_at': firestore.SERVER_TIMESTAMP
                }
                
                if details.get('events'):
                    add_log(f"- Collected {len(details['events'])} events")
                if details.get('lineups'):
                    add_log(f"- Collected {len(details['lineups'])} lineups")
                if details.get('statistics'):
                    add_log(f"- Collected statistics")
                if details.get('players'):
                    total_players = sum(len(team_players) for team_players in details['players'])
                    add_log(f"- Collected data for {total_players} players")
                
                fixture_ref = db.collection('fixtures').document(str(fixture_id))
                batch.set(fixture_ref, fixture_data)
            
            batch.commit()
            add_log(f"Committed batch {i+1} of {len(chunks)}")
            
            total_processed += len(chunk)
            progress = (total_processed / total_fixtures) * 100
            global_state.current_progress = f"Progress: {progress:.1f}% ({total_processed}/{total_fixtures})"

        add_log("Data collection completed successfully!")
        global_state.is_running = False
        
    except Exception as e:
        error_message = str(e)
        add_log(f"ERROR: {error_message}")
        global_state.current_error = error_message
        global_state.is_running = False

def setup_data_collection_callbacks(app, api):
    @app.callback(
        Output('country-selector', 'options'),
        Input('country-selector', 'search_value')
    )
    def update_countries(search_value):
        try:
            data = make_api_request(
                f"{api.base_url}/countries",
                headers=api.headers
            )
            if data.get('response'):
                countries = data['response']
                options = [
                    {'label': f"{country['name']} {country.get('flag', '')}", 
                     'value': country['name']} 
                    for country in countries
                ]
                logger.info(f"Retrieved {len(options)} countries")
                return options
            return []
        except Exception as e:
            logger.error(f"Error in update_countries: {e}")
            return []

    @app.callback(
        Output('league-selector', 'options'),
        Input('country-selector', 'value')
    )
    def update_leagues(country):
        if not country:
            raise PreventUpdate
        try:
            data = make_api_request(
                f"{api.base_url}/leagues",
                headers=api.headers,
                params={'country': country}
            )
            if data.get('response'):
                leagues = data['response']
                options = [
                    {'label': f"{league['league']['name']}", 
                     'value': league['league']['id']} 
                    for league in leagues
                ]
                logger.info(f"Retrieved {len(options)} leagues for {country}")
                return options
            return []
        except Exception as e:
            logger.error(f"Error in update_leagues: {e}")
            return []

    @app.callback(
        Output('season-selector', 'options'),
        Input('league-selector', 'value')
    )
    def update_seasons(league_id):
        if not league_id:
            raise PreventUpdate
        try:
            data = make_api_request(
                f"{api.base_url}/leagues/seasons",
                headers=api.headers
            )
            if data.get('response'):
                seasons = data['response']
                options = [
                    {'label': str(season), 'value': season} 
                    for season in sorted(seasons, reverse=True)
                ]
                logger.info(f"Retrieved {len(options)} seasons")
                return options
            return []
        except Exception as e:
            logger.error(f"Error in update_seasons: {e}")
            return []

    @app.callback(
        Output('status-store', 'data'),
        Input('collect-data-button', 'n_clicks'),
        [State('league-selector', 'value'),
         State('season-selector', 'value')],
        prevent_initial_call=True
    )
    def start_collection(n_clicks, league_id, season):
        if not n_clicks or not league_id or not season:
            raise PreventUpdate
            
        if not global_state.is_running:
            global_state.is_running = True
            global_state.current_status = "Starting collection..."
            global_state.current_progress = ""
            global_state.current_error = ""
            global_state.log_messages = []
            
            # Start collection in a separate thread
            thread = threading.Thread(
                target=process_collection,
                args=(api, league_id, season)
            )
            thread.start()
            
        return {'status': 'started'}

    @app.callback(
        [Output('collection-status', 'children'),
         Output('progress-display', 'children'),
         Output('error-display', 'children'),
         Output('progress-log', 'children')],
        Input('interval-component', 'n_intervals')
    )
    def update_status(n):
        return (
            global_state.current_status,
            global_state.current_progress,
            global_state.current_error,
            global_state.log_messages
        )