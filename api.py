import requests
import logging

from config import ALL_LEAGUES, LEAGUE_NAMES

logger = logging.getLogger(__name__)

class FootballAPI:
    def __init__(self, api_key, base_url):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {'x-apisports-key': api_key}

    def fetch_teams(self, league_id, season='2024'):
        if league_id == ALL_LEAGUES:
            all_teams = []
            for lid in LEAGUE_NAMES.keys():
                 if lid != ALL_LEAGUES:
                    teams = self.fetch_teams(lid, season)
                    all_teams.extend(teams)
            return all_teams
    
        url = f"{self.base_url}/teams"
        params = {
            'league': league_id,
            'season': season
        }
        
        response = requests.get(url, headers=self.headers, params=params)
        if response.status_code == 200:
            return response.json().get('response', [])
        return []

    def fetch_fixtures(self, league_id, season='2024', team_id=None):
        if league_id == ALL_LEAGUES:
            all_fixtures = []
            for lid in LEAGUE_NAMES.keys():
                 if lid != ALL_LEAGUES:
                    fixtures = self.fetch_fixtures(lid, season, team_id)
                    all_fixtures.extend(fixtures)
            return all_fixtures
        
        url = f"{self.base_url}/fixtures"
        params = {
            'league': league_id,
            'season': season
        }
        if team_id:
            params['team'] = team_id
            
        response = requests.get(url, headers=self.headers, params=params)
        if response.status_code == 200:
            return response.json().get('response', [])
        return []