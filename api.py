from datetime import datetime, timedelta
import time
import requests
import logging
from functools import lru_cache
import json
from typing import Dict, Any, Optional

from config import ALL_LEAGUES, PERF_DIFF_THRESHOLD
from league_names import LEAGUE_NAMES
from sport_analyzers.form_analyzer import FormAnalyzer

logger = logging.getLogger(__name__)

class FootballAPI:
    def __init__(self, api_key, base_url):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {'x-apisports-key': api_key}
        self.logger = logging.getLogger(__name__)
        self._initialize_cache()
        
    def _initialize_cache(self):
        """Initialize different cache stores with different durations"""
        self.cache = {
            'short': {'data': {}, 'duration': timedelta(minutes=15)},  # 15 minutes for volatile data
            'medium': {'data': {}, 'duration': timedelta(hours=6)},    # 6 hours for semi-stable data
            'long': {'data': {}, 'duration': timedelta(hours=24)},     # 24 hours for stable data
        }
        
    def _get_from_cache(self, key: str, cache_type: str = 'short') -> Optional[Any]:
        """Get data from cache with specified duration type"""
        cache_store = self.cache[cache_type]['data']
        if key in cache_store:
            data, timestamp = cache_store[key]
            if datetime.now() - timestamp < self.cache[cache_type]['duration']:
                return data
            del cache_store[key]
        return None

    def _set_cache(self, key: str, data: Any, cache_type: str = 'short'):
        """Set data in cache with specified duration type"""
        self.cache[cache_type]['data'][key] = (data, datetime.now())

    def _batch_request(self, url: str, params_list: list) -> Dict:
        """Make batch requests and handle rate limiting"""
        results = {}
        for params in params_list:
            cache_key = f"{url}_{json.dumps(params, sort_keys=True)}"
            cached_data = self._get_from_cache(cache_key)
            
            if cached_data:
                results[json.dumps(params)] = cached_data
                continue

            try:
                response = requests.get(url, headers=self.headers, params=params)
                if response.status_code == 200:
                    data = response.json()
                    self._set_cache(cache_key, data)
                    results[json.dumps(params)] = data
                elif response.status_code == 429:  # Rate limit
                    time.sleep(60)  # Wait a minute before retrying
                    response = requests.get(url, headers=self.headers, params=params)
                    if response.status_code == 200:
                        data = response.json()
                        self._set_cache(cache_key, data)
                        results[json.dumps(params)] = data
                time.sleep(0.2)  # Small delay between requests
            except Exception as e:
                self.logger.error(f"Error in batch request: {str(e)}")
                continue
                
        return results
    
    
    async def get_countries(self):
        """Get list of available countries"""
        response = await self._make_request('/countries')
        return response.get('response', [])

    async def get_leagues(self, country=None):
        """Get leagues for a country"""
        params = {'country': country} if country else {}
        response = await self._make_request('/leagues', params)
        return response.get('response', [])

    async def get_seasons(self, league_id):
        """Get available seasons for a league"""
        response = await self._make_request(f'/leagues/seasons')
        return response.get('response', [])

    async def get_fixtures(self, league_id, season, status=None):
        """Get fixtures for a league and season"""
        params = {
            'league': league_id,
            'season': season
        }
        if status:
            params['status'] = status
        response = await self._make_request('/fixtures', params)
        return response.get('response', [])

    async def get_fixtures_by_ids(self, ids):
        """Get detailed fixtures data by IDs"""
        response = await self._make_request(f'/fixtures', {'ids': ids})
        return response.get('response', [])
    
    def fetch_all_teams(self, league_names, matches_count=3):
        """
        Fetch all teams across all leagues with form analysis
        
        Args:
            league_names: Dictionary of league IDs and names
            matches_count: Number of recent matches to analyze for form
            
        Returns:
            list: List of teams with their form analysis
        """
        logger.debug(f"Fetching all teams for {len(league_names)} leagues")
        all_teams = []

        try:
            # Process ALL_LEAGUES case
            if league_names.get(ALL_LEAGUES):
                standings = self.fetch_standings(ALL_LEAGUES)
                
                if not standings:
                    logger.warning("No standings available for ALL_LEAGUES")
                    return []

                # Process each league
                for league_id, league_standings in standings.items():
                    league_info = league_names.get(league_id, {})
                    if not league_info:
                        logger.warning(f"No information for league {league_id}")
                        continue

                    try:
                        # Get standings data safely
                        response = league_standings.get('response', [{}])[0]
                        standings_data = response.get('league', {}).get('standings', [[]])[0]
                        
                        # Get fixtures with caching
                        fixtures = self.fetch_fixtures(league_id)

                        # Process each team
                        for team in standings_data:
                            try:
                                team_data = team.get('team', {})
                                team_id = team_data.get('id')
                                if not team_id:
                                    continue

                                team_name = team_data.get('name', 'Unknown')
                                matches_played = team.get('all', {}).get('played', 0)
                                
                                if matches_played == 0:
                                    continue

                                actual_points = team.get('points', 0)
                                current_ppg = actual_points / matches_played if matches_played > 0 else 0

                                # Analyze team form
                                form_data = FormAnalyzer.analyze_team_form(fixtures, team_id, matches_count)
                                
                                form_points = form_data['points']
                                form_matches = form_data['matches_analyzed']
                                form_ppg = form_points / matches_count if form_matches > 0 else 0
                                form_vs_actual_diff = form_ppg - current_ppg
                                
                                # Include team info
                                performance_diff = round(form_vs_actual_diff, 2)
                                if abs(performance_diff) > PERF_DIFF_THRESHOLD:  # Filter teams here
                                    team_info = {
                                        'team_id': team_id,
                                        'team': team_name,
                                        'league': f"{league_info.get('flag', '')} {league_info.get('name', '')}",
                                        'current_position': team.get('rank', 0),
                                        'matches_played': matches_played,
                                        'current_points': actual_points,
                                        'current_ppg': round(current_ppg, 2),
                                        'form': ' '.join(form_data['form']),
                                        'form_points': form_points,
                                        'form_ppg': round(form_ppg, 2),
                                        'performance_diff': round(form_vs_actual_diff, 2),
                                        'goals_for': form_data['goals_for'],
                                        'goals_against': form_data['goals_against']
                                    }
                                    
                                    all_teams.append(team_info)

                            except Exception as e:
                                logger.error(f"Error processing team {team_data.get('name', 'Unknown')}: {str(e)}")
                                continue

                    except Exception as e:
                        logger.error(f"Error processing league {league_id}: {str(e)}")
                        continue

            else:
                # Process individual leagues
                for league_id, league_info in league_names.items():
                    if not isinstance(league_id, int):
                        continue

                    try:
                        standings = self.fetch_standings(league_id)
                        if not standings or not standings.get('response'):
                            logger.warning(f"No standings for league {league_id}")
                            continue

                        standings_data = standings['response'][0]['league']['standings'][0]
                        fixtures = self.fetch_fixtures(league_id)

                        for team in standings_data:
                            try:
                                team_data = team.get('team', {})
                                team_id = team_data.get('id')
                                if not team_id:
                                    continue

                                team_name = team_data.get('name', 'Unknown')
                                matches_played = team.get('all', {}).get('played', 0)
                                
                                if matches_played == 0:
                                    continue

                                actual_points = team.get('points', 0)
                                current_ppg = actual_points / matches_played if matches_played > 0 else 0

                                # Analyze team form
                                form_data = FormAnalyzer.analyze_team_form(fixtures, team_id, matches_count)
                                
                                form_points = form_data['points']
                                form_matches = form_data['matches_analyzed']
                                form_ppg = form_points / matches_count if form_matches > 0 else 0
                                form_vs_actual_diff = form_ppg - current_ppg
                                 # Include team info
                                performance_diff = round(form_vs_actual_diff, 2)
                                if abs(performance_diff) > PERF_DIFF_THRESHOLD:  # Filter teams here

                                    team_info = {
                                        'team_id': team_id,
                                        'team': team_name,
                                        'league': f"{league_info.get('flag', '')} {league_info.get('name', '')}",
                                        'current_position': team.get('rank', 0),
                                        'matches_played': matches_played,
                                        'current_points': actual_points,
                                        'current_ppg': round(current_ppg, 2),
                                        'form': ' '.join(form_data['form']),
                                        'form_points': form_points,
                                        'form_ppg': round(form_ppg, 2),
                                        'performance_diff': round(form_vs_actual_diff, 2),
                                        'goals_for': form_data['goals_for'],
                                        'goals_against': form_data['goals_against']
                                    }
                                    
                                    all_teams.append(team_info)

                            except Exception as e:
                                logger.error(f"Error processing team {team_data.get('name', 'Unknown')}: {str(e)}")
                                continue

                    except Exception as e:
                        logger.error(f"Error processing league {league_id}: {str(e)}")
                        continue

        except Exception as e:
            logger.error(f"Error in fetch_all_teams: {str(e)}")
            return []

        # Sort by absolute performance difference
        return sorted(all_teams, key=lambda x: abs(x.get('performance_diff', 0)), reverse=True)

    def fetch_standings(self, league_id):
        """Optimized standings fetch with better caching"""
        cache_key = f'standings_{league_id}'
        cached_data = self._get_from_cache(cache_key, 'medium')  # Standings change less frequently
        if cached_data:
            return cached_data

        url = f"{self.base_url}/standings"
        if league_id == ALL_LEAGUES:
            # Batch request for all leagues
            params_list = [
                {"league": lid, "season": 2024}
                for lid in LEAGUE_NAMES.keys()
                if isinstance(lid, int) and lid != ALL_LEAGUES
            ]
            results = self._batch_request(url, params_list)
            
            all_standings = {}
            for params_str, data in results.items():
                params = json.loads(params_str)
                all_standings[params['league']] = data
                
            self._set_cache(cache_key, all_standings, 'medium')
            return all_standings
        else:
            params = {"league": league_id, "season": 2024}
            results = self._batch_request(url, [params])
            data = results.get(json.dumps(params))
            if data:
                self._set_cache(cache_key, data, 'medium')
                return data
        return None

    def fetch_fixtures(self, league_id, season='2024', team_id=None, fixture_id=None):
        """Optimized fixtures fetch with smarter caching"""
        cache_key = f'fixtures_{league_id}_{team_id}_{fixture_id}'
        
        # Use longer cache duration for historical fixtures
        cache_type = 'long' if not fixture_id else 'short'
        cached_data = self._get_from_cache(cache_key, cache_type)
        if cached_data:
            return cached_data

        url = f"{self.base_url}/fixtures"
        
        if fixture_id:
            params = {'id': fixture_id}
            results = self._batch_request(url, [params])
            data = results.get(json.dumps(params), {}).get('response', [])
            self._set_cache(cache_key, data, cache_type)
            return data

        if league_id == ALL_LEAGUES:
            params_list = [
                {'league': lid, 'season': season, **({"team": team_id} if team_id else {})}
                for lid in LEAGUE_NAMES.keys()
                if isinstance(lid, int) and lid != ALL_LEAGUES
            ]
            results = self._batch_request(url, params_list)
            
            all_fixtures = []
            for result in results.values():
                if result and result.get('response'):
                    all_fixtures.extend(result['response'])
                    
            self._set_cache(cache_key, all_fixtures, cache_type)
            return all_fixtures
        
        params = {
            'league': league_id,
            'season': season,
            **({"team": team_id} if team_id else {})
        }
        results = self._batch_request(url, [params])
        data = results.get(json.dumps(params), {}).get('response', [])
        self._set_cache(cache_key, data, cache_type)
        return data

    def fetch_team_statistics(self, league_id, team_id, season='2024'):
        """Optimized team statistics fetch with null safety"""
        cache_key = f'team_stats_{league_id}_{team_id}'
        cached_data = self._get_from_cache(cache_key, 'medium')
        if cached_data:
            return cached_data
            
        url = f"{self.base_url}/teams/statistics"
        params = {
            'league': league_id,
            'team': team_id,
            'season': season
        }
        
        try:
            results = self._batch_request(url, [params])
            data = results.get(json.dumps(params), {}).get('response', {})
            
            # Ensure we have valid data structure
            if not data:
                self.logger.warning(f"No team statistics found for team {team_id} in league {league_id}")
                return {}
                
            # Ensure all required fields have default values
            stats = {
                'form': data.get('form', ''),
                'fixtures': data.get('fixtures', {}),
                'goals': data.get('goals', {}),
                'biggest': data.get('biggest', {}),
                'clean_sheet': data.get('clean_sheet', {}),
                'failed_to_score': data.get('failed_to_score', {}),
                'penalty': data.get('penalty', {}),
                'lineups': data.get('lineups', []),
                'cards': data.get('cards', {})
            }
            
            self._set_cache(cache_key, stats, 'medium')
            return stats
            
        except Exception as e:
            self.logger.error(f"Error fetching team statistics for {team_id}: {str(e)}")
            return {}

    def fetch_player_statistics(self, league_id, team_id, season='2024'):
        """Optimized player statistics fetch with batch processing"""
        cache_key = f'player_stats_{league_id}_{team_id}'
        cached_data = self._get_from_cache(cache_key, 'medium')
        if cached_data:
            return cached_data

        # Fetch squad first
        squad_url = f"{self.base_url}/players/squads"
        squad_params = {'team': team_id}
        squad_results = self._batch_request(squad_url, [squad_params])
        squad_data = squad_results.get(json.dumps(squad_params))
        
        if not squad_data or not squad_data.get('response'):
            return []

    def fetch_match_odds(self, fixture_id):
        """Fetch match odds with very short caching duration and null safety"""
        cache_key = f'odds_{fixture_id}'
        cached_data = self._get_from_cache(cache_key, 'short')  # Short cache for odds
        if cached_data:
            return cached_data
            
        url = f"{self.base_url}/odds"
        params = {
            "fixture": fixture_id,
            "bookmaker": "8",  # Bet365
        }
        
        try:
            results = self._batch_request(url, [params])
            data = results.get(json.dumps(params))
            
            if data and data.get('response'):
                response_data = data['response']
                if not response_data:
                    self.logger.warning(f"No odds data found for fixture {fixture_id}")
                    return {'home': '0', 'draw': '0', 'away': '0'}
                    
                odds_data = response_data[0]
                if not odds_data.get('bookmakers'):
                    self.logger.warning(f"No bookmakers found for fixture {fixture_id}")
                    return {'home': '0', 'draw': '0', 'away': '0'}
                    
                bookmaker = odds_data['bookmakers'][0]
                if not bookmaker.get('bets'):
                    self.logger.warning(f"No bets found for fixture {fixture_id}")
                    return {'home': '0', 'draw': '0', 'away': '0'}
                    
                bets = bookmaker['bets'][0]
                if not bets.get('values') or len(bets['values']) < 3:
                    self.logger.warning(f"Incomplete odds values for fixture {fixture_id}")
                    return {'home': '0', 'draw': '0', 'away': '0'}
                    
                odds = {
                    'home': bets['values'][0].get('odd', '0'),
                    'draw': bets['values'][1].get('odd', '0'),
                    'away': bets['values'][2].get('odd', '0')
                }
                self._set_cache(cache_key, odds, 'short')
                return odds
                
        except Exception as e:
            self.logger.error(f"Error parsing odds for fixture {fixture_id}: {str(e)}")
            
        return {'home': '0', 'draw': '0', 'away': '0'}

    @staticmethod
    def format_odds(odds_value):
        """Format odds value to decimal format with 2 decimal places"""
        try:
            return f"{float(odds_value):.2f}"
        except (ValueError, TypeError):
            return "N/A"

        # Batch process player statistics
        squad = squad_data['response'][0]['players']
        stats_url = f"{self.base_url}/players"
        params_list = [
            {'id': player['id'], 'league': league_id, 'season': season}
            for player in squad
        ]
        
        # Split into smaller batches to avoid overwhelming the API
        batch_size = 5
        all_stats = []
        
        for i in range(0, len(params_list), batch_size):
            batch_params = params_list[i:i + batch_size]
            results = self._batch_request(stats_url, batch_params)
            
            for result in results.values():
                if result and result.get('response'):
                    all_stats.extend(result['response'])
            
            time.sleep(1)  # Pause between batches
            
        self._set_cache(cache_key, all_stats, 'medium')
        return all_stats
        
   
        
    def fetch_next_fixtures(self, league_id, season='2024'):
        """Fetch next round of fixtures for a league with short-term caching"""
        cache_key = f'next_fixtures_{league_id}_{season}'
        cached_data = self._get_from_cache(cache_key, 'short')  # Short cache for upcoming fixtures
        if cached_data:
            return cached_data
            
        url = f"{self.base_url}/fixtures"
        params = {
            'league': league_id,
            'season': season,
            'next': 10  # Fetch next 10 matches to ensure we get the full round
        }
        
        try:
            results = self._batch_request(url, [params])
            data = results.get(json.dumps(params), {}).get('response', [])
            
            if data:
                # Group by round and get the next round
                rounds = {}
                for fix in data:
                    round_num = fix['league']['round']
                    if round_num not in rounds:
                        rounds[round_num] = []
                    rounds[round_num].append(fix)
                
                # Get the earliest round
                next_round = next(iter(rounds.values())) if rounds else []
                self._set_cache(cache_key, next_round, 'short')  # Short cache duration for upcoming fixtures
                return next_round
                
        except Exception as e:
            self.logger.error(f"Error fetching next fixtures: {str(e)}")
            
        return []