
from dash import html, dcc, ctx
import dash
from dash.dependencies import Input, Output, State, ALL
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

from dash import dcc, html
from sport_layouts.fixtures_tab_firestore import create_selection_row

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
        self.min_interval = 60.0 / calls_per_minute

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
        # Get events
        events_data = make_api_request(
            f"{api.base_url}/fixtures/events",
            headers=api.headers,
            params={'fixture': fixture_id},
            rate_limiter=rate_limiter
        )
        
        # Get lineups
        lineups_data = make_api_request(
            f"{api.base_url}/fixtures/lineups",
            headers=api.headers,
            params={'fixture': fixture_id},
            rate_limiter=rate_limiter
        )
        
        # Get statistics
        stats_data = make_api_request(
            f"{api.base_url}/fixtures/statistics",
            headers=api.headers,
            params={'fixture': fixture_id},
            rate_limiter=rate_limiter
        )
        
        # Get players
        players_data = make_api_request(
            f"{api.base_url}/fixtures/players",
            headers=api.headers,
            params={'fixture': fixture_id},
            rate_limiter=rate_limiter
        )
        
        return {
            'events': events_data.get('response', []),
            'lineups': lineups_data.get('response', []),
            'statistics': stats_data.get('response', []),
            'players': players_data.get('response', [])
        }
    except Exception as e:
        logger.error(f"Error collecting details for fixture {fixture_id}: {e}")
        return {}

def process_collection(api, league_id, season):
    try:
        rate_limiter = RateLimiter(30)
        db = firestore.client()
        
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
        
        chunk_size = 20
        chunks = [fixtures[i:i + chunk_size] for i in range(0, len(fixtures), chunk_size)]
        total_processed = 0

        for i, chunk in enumerate(chunks):
            add_log(f"\nProcessing chunk {i+1} of {len(chunks)}")
            batch = db.batch()
            
            for fixture in chunk:
                fixture_id = str(fixture['fixture']['id'])
                
                # Check if fixture exists and when it was last updated
                doc_ref = db.collection('fixtures').document(fixture_id)
                doc = doc_ref.get()
                
                if doc.exists:
                    fixture_data = doc.to_dict()
                    fixture_date = fixture['fixture']['date']
                    stored_date = fixture_data.get('fixture', {}).get('date')
                    
                    if fixture_date == stored_date:
                        add_log(f"Skipping fixture {fixture_id} - already up to date")
                        continue
                
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
                
                batch.set(doc_ref, fixture_data)
                total_processed += 1
            
            if total_processed > 0:
                batch.commit()
                add_log(f"Committed batch {i+1} of {len(chunks)}")
            
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
        [Output('selection-rows-container', 'children'),
         Output('rows-store', 'data'),
         Output('add-row-button', 'disabled')],
        Input('add-row-button', 'n_clicks'),
        State('rows-store', 'data')
    )
    def add_selection_row(n_clicks, rows_data):
        if not n_clicks:
            raise PreventUpdate
            
        num_rows = rows_data['num_rows']
        if num_rows >= 5:
            return dash.no_update, dash.no_update, True
            
        new_row = create_selection_row(num_rows)
        existing_rows = [create_selection_row(i) for i in range(num_rows)]
        rows_data['num_rows'] = num_rows + 1
        
        return existing_rows + [new_row], rows_data, num_rows + 1 >= 5
    
    @app.callback(
        Output({'type': 'country-selector', 'index': ALL}, 'options'),
        Input({'type': 'country-selector', 'index': ALL}, 'search_value')
    )
    def update_countries(search_values):
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
                return [options] * len(search_values)
            return [[]] * len(search_values)
        except Exception as e:
            logger.error(f"Error in update_countries: {e}")
            return [[]] * len(search_values)
        
        

    @app.callback(
        Output({'type': 'league-selector', 'index': ALL}, 'options'),
        Input({'type': 'country-selector', 'index': ALL}, 'value')
    )
    def update_leagues(countries):
        outputs = []
        for country in countries:
            if not country:
                outputs.append([])
                continue
                
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
                    outputs.append(options)
                else:
                    outputs.append([])
            except Exception as e:
                logger.error(f"Error in update_leagues: {e}")
                outputs.append([])
        
        return outputs
    
    
    

    @app.callback(
        Output({'type': 'season-selector', 'index': ALL}, 'options'),
        Input({'type': 'league-selector', 'index': ALL}, 'value')
    )
    def update_seasons(league_ids):
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
                return [options] * len(league_ids)
            return [[]] * len(league_ids)
        except Exception as e:
            logger.error(f"Error in update_seasons: {e}")
            return [[]] * len(league_ids)
    
    @app.callback(
        [Output('collect-data-button', 'disabled'),
         Output('error-display', 'children')],
        [Input({'type': 'country-selector', 'index': ALL}, 'value'),
         Input({'type': 'league-selector', 'index': ALL}, 'value'),
         Input({'type': 'season-selector', 'index': ALL}, 'value')]
    )
    def update_collect_button_state(countries, leagues, seasons):
        # Enable button only if all dropdowns in all rows have values
        if not countries or not leagues or not seasons:
            return True
        
        error_message = ""
        for season in seasons:
            if season and str(season) != "2024":
                error_message = "Only season 2024 is allowed!"
                return True, html.Div(error_message, style={'color': 'red', 'fontWeight': 'bold'})
            
        for country, league, season in zip(countries, leagues, seasons):
            if not country or not league or not season:
                return True, error_message
        return False,error_message
        
        

    @app.callback(
        Output('status-store', 'data'),
        Input('collect-data-button', 'n_clicks'),
        [State({'type': 'league-selector', 'index': ALL}, 'value'),
         State({'type': 'season-selector', 'index': ALL}, 'value')],
        prevent_initial_call=True
    )
    def start_collection(n_clicks, league_ids, seasons):
        if not n_clicks or not league_ids or not seasons:
            raise PreventUpdate
            
        if not global_state.is_running:
            global_state.is_running = True
            global_state.current_status = "Starting collection..."
            global_state.current_progress = ""
            global_state.current_error = ""
            global_state.log_messages = []
            
            # Process each selection in sequence
            for league_id, season in zip(league_ids, seasons):
                if league_id and season:  # Only process complete selections
                    thread = threading.Thread(
                        target=process_collection,
                        args=(api, league_id, season)
                    )
                    thread.start()
                    thread.join()  # Wait for each collection to complete before starting next
            
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