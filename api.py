import time
import requests
import logging

from config import ALL_LEAGUES, LEAGUE_NAMES

logger = logging.getLogger(__name__)

class FootballAPI:
    def __init__(self, api_key, base_url):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {'x-apisports-key': api_key}
        self.logger = logging.getLogger(__name__)
        
    def fetch_standings(self, league_id):
        url = f"{self.base_url}/standings"
        params = {
            "league": league_id,
            "season": 2024
        }
        try:
            response = requests.get(url, headers=self.headers, params=params)
            return response.json() if response.status_code == 200 else None
        except Exception as e:
            self.logger.error(f"Error fetching standings: {str(e)}")
            return None
        
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
    def _make_request(self, url, params=None):
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API request failed: {str(e)}")
            return None

    def fetch_fixtures(self, league_id, season='2024', team_id=None, fixture_id=None):
        # If fixture_id is provided, fetch specific fixture
        if fixture_id is not None:
            url = f"{self.base_url}/fixtures"
            params = {'id': fixture_id}
            response = requests.get(url, headers=self.headers, params=params)
            if response.status_code == 200:
                return response.json().get('response', [])
            return []

        # Otherwise, fetch fixtures by league/team
        if league_id == ALL_LEAGUES:
            all_fixtures = []
            for lid in LEAGUE_NAMES:
                # Skip non-numeric and ALL_LEAGUES entries
                if isinstance(lid, int) and lid != ALL_LEAGUES:
                    try:
                        fixtures = self.fetch_fixtures(lid, season, team_id)
                        if fixtures:
                            all_fixtures.extend(fixtures)
                    except Exception as e:
                        self.logger.error(f"Error fetching fixtures for league {lid}: {str(e)}")
                        continue
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

    def fetch_next_fixtures(self, league_id, season='2024'):
        """Fetch next round of fixtures for a league"""
        url = f"{self.base_url}/fixtures"
        params = {
            'league': league_id,
            'season': season,
            'next': 10  # Fetch next 10 matches to ensure we get the full round
        }
        
        response = requests.get(url, headers=self.headers, params=params)
        if response.status_code == 200:
            fixtures = response.json().get('response', [])
            if fixtures:
                # Group by round and get the next round
                rounds = {}
                for fix in fixtures:
                    round_num = fix['league']['round']
                    if round_num not in rounds:
                        rounds[round_num] = []
                    rounds[round_num].append(fix)
                
                # Return the earliest round
                return next(iter(rounds.values())) if rounds else []
        return []

    def fetch_player_statistics(self, league_id, team_id, season='2024'):
        """Fetch player statistics for a team"""
        # First try to get players list
        players_url = f"{self.base_url}/players/squads"
        squad_params = {
            'team': team_id
        }
        
        logger.info(f"Fetching squad for team {team_id}")
        
        try:
            squad_response = requests.get(players_url, headers=self.headers, params=squad_params)
            if squad_response.status_code != 200:
                logger.error(f"Error fetching squad. Status: {squad_response.status_code}")
                return []
                
            squad_data = squad_response.json()
            if not squad_data.get('response'):
                logger.error("No squad data found")
                return []
                
            # Get squad players
            squad = squad_data['response'][0]['players']
            logger.info(f"Found {len(squad)} players in squad")
            
            # Now fetch statistics for each player
            all_player_stats = []
            for player in squad:
                player_id = player['id']
                
                # Get player statistics
                stats_url = f"{self.base_url}/players"
                stats_params = {
                    'id': player_id,
                    'league': league_id,
                    'season': season
                }
                
                logger.info(f"Fetching stats for player {player['name']} (ID: {player_id})")
                
                stats_response = requests.get(stats_url, headers=self.headers, params=stats_params)
                if stats_response.status_code == 200:
                    stats_data = stats_response.json()
                    if stats_data.get('response'):
                        logger.info(f"Found statistics for {player['name']}")
                        all_player_stats.extend(stats_data['response'])
                else:
                    logger.warning(f"Could not get stats for {player['name']}")
                
                # Add small delay to avoid rate limits
                time.sleep(0.1)
            
            return all_player_stats
            
        except Exception as e:
            logger.error(f"Error fetching player statistics: {str(e)}")
            return []

    def fetch_team_statistics(self, league_id, team_id, season='2024'):
        """Fetch team statistics"""
        url = f"{self.base_url}/teams/statistics"
        params = {
            'league': league_id,
            'team': team_id,
            'season': season
        }
        
        logger.debug(f"Fetching team stats with params: {params}")
        response = requests.get(url, headers=self.headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            logger.debug(f"Team stats response: {data}")
            return data.get('response', {})
        else:
            logger.error(f"Error fetching team stats. Status code: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return {}
    def fetch_match_odds(self, fixture_id):
        url = f"{self.base_url}/odds"
        params = {
            "fixture": fixture_id,
            "bookmaker": "8",  # Bet365
        }
        
        try:
            response = self._make_request(url, params)
            #print(f"Odds API Response for fixture {fixture_id}:", response)  # Debug print
            
            if response and response.get('response'):
                odds_data = response['response'][0]
                #print("Odds data:", odds_data)  # Debug print
                return {
                    'home': odds_data['bookmakers'][0]['bets'][0]['values'][0]['odd'],
                    'draw': odds_data['bookmakers'][0]['bets'][0]['values'][1]['odd'],
                    'away': odds_data['bookmakers'][0]['bets'][0]['values'][2]['odd']
                }
        except Exception as e:
            self.logger.error(f"Error parsing odds for fixture {fixture_id}: {str(e)}")
            print(f"Error details: {str(e)}")  # Debug print
            return None
    def format_odds(odds_value):
        """
        Format odds value to decimal format with 2 decimal places
        """
        try:
            return f"{float(odds_value):.2f}"
        except (ValueError, TypeError):
            return "N/A"