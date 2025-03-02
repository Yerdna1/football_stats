from collections import defaultdict
import json
import os
import time
from typing import Dict, List, Optional
from venv import logger
from dotenv import load_dotenv
import requests

load_dotenv()  # Load environment variables from .env file

API_KEY = os.getenv('FOOTBALL_API_KEY')  # Instead of hardcoding
BASE_URL = os.getenv('BASE_URL')
CALLS_PER_MINUTE=os.getenv('CALLS_PER_MINUTE')



ALL_LEAGUES = -1  # Special value for all leagues
PERF_DIFF_THRESHOLD = 0.75

class FootballDataFetcher:
    def __init__(self):
        self.api_key = os.getenv('FOOTBALL_API_KEY')
        self.calls_per_minute = int(os.getenv('CALLS_PER_MINUTE', '30'))
        self.headers = {
            'x-rapidapi-key': self.api_key,
            'x-rapidapi-host': 'v3.football.api-sports.io'
        }

    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make API request with rate limiting"""
        try:
            time.sleep(60 / self.calls_per_minute)  # Rate limiting
            url = f"https://v3.football.api-sports.io/{endpoint}"
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return None

    def get_countries(self) -> List[Dict]:
        """Get all available countries from the API"""
        response = self._make_request("countries")
        if not response or not response.get('response'):
            logger.error("Failed to fetch countries")
            return []
        return response['response']

    def get_leagues_for_country(self, country_name: str) -> List[Dict]:
        """Get all leagues for a specific country"""
        response = self._make_request("leagues", {
            "country": country_name,
            "current": True  # Only get currently active leagues
        })
        if not response or not response.get('response'):
            logger.error(f"Failed to fetch leagues for {country_name}")
            return []
        
        # Sort leagues by tier/importance
        leagues = response['response']
        # Remove duplicate leagues (same id)
        seen_ids = set()
        unique_leagues = []
        for league in leagues:
            league_id = league['league']['id']
            if league_id not in seen_ids:
                seen_ids.add(league_id)
                unique_leagues.append(league)
        
        return unique_leagues

    def check_league_activity(self, league_id: int, season: int) -> Dict:
        """Check if a league has active fixtures and players for given season"""
        # Get fixtures for the season
        fixtures = self._make_request("fixtures", {
            "league": league_id,
            "season": season
        })

        if not fixtures or not fixtures.get('response'):
            return {"active": False, "fixture_count": 0}

        # Check first fixture for players
        for fixture in fixtures['response'][:1]:
            fixture_id = fixture['fixture']['id']
            players = self._make_request("fixtures/players", {
                "fixture": fixture_id
            })
            if players and players.get('response'):
                return {
                    "active": True,
                    "fixture_count": len(fixtures['response'])
                }

        return {"active": False, "fixture_count": 0}

    def find_active_leagues(self, season: int = 2024) -> List[Dict]:
        """Find all leagues with active fixtures and players for given season"""
        active_leagues = []
        countries = self.get_countries()
        
        print(f"\nScanning countries for active leagues in {season} season...")
        print("="*50)

        for country in countries:
            country_name = country['name']
            print(f"\nChecking leagues in {country['flag']} {country_name}")
            
            leagues = self.get_leagues_for_country(country_name)
            if not leagues:
                print(f"  No leagues found for {country_name}")
                continue
                
            print(f"  Found {len(leagues)} leagues to check")
            
            for league in leagues:
                league_id = league['league']['id']
                league_name = league['league']['name']
                league_type = league['league'].get('type', 'Unknown')
                
                print(f"  - Checking {league_name} ({league_type})")
                
                activity = self.check_league_activity(league_id, season)
                if activity['active']:
                    active_league = {
                        "id": league_id,
                        "name": league_name,
                        "country": country_name,
                        "flag": country['flag'],
                        "type": league_type,
                        "fixture_count": activity['fixture_count']
                    }
                    active_leagues.append(active_league)
                    print(f"    ✅ Added {league_name} - {activity['fixture_count']} fixtures found")
                else:
                    print(f"    ❌ No active fixtures/players found")

        return active_leagues

def generate_league_names_dict(active_leagues: List[Dict]) -> str:
    """Generate LEAGUE_NAMES dictionary string in the required format"""
    # Start with the ALL_LEAGUES entry
    output_lines = []
    output_lines.append("LEAGUE_NAMES = {")
    output_lines.append("       ALL_LEAGUES: {\"name\": \"All Leagues\", \"flag\": \"🌍\", \"country\": \"Global\"},  # Use -1 here")
    output_lines.append("")
    
    # Group leagues by country to maintain better organization
    leagues_by_country = defaultdict(list)
    for league in active_leagues:
        if league['type'].lower() == 'league':
            leagues_by_country[league['country']].append(league)
    
    # Add each league entry with proper indentation
    sorted_countries = sorted(leagues_by_country.keys())
    for country in sorted_countries:
        for league in leagues_by_country[country]:
            entry = f"   {league['id']}: {{\"name\": \"{league['name']}\", \"flag\": \"{league['flag']}\", \"country\": \"{league['country']}\"}}"
            output_lines.append(entry + ",")
    
    # Remove the last comma
    if output_lines[-1].endswith(","):
        output_lines[-1] = output_lines[-1][:-1]
    
    output_lines.append("}")
    return "\n".join(output_lines)


   

    
""" LEAGUE_NAMES = {
       ALL_LEAGUES: {"name": "All Leagues", "flag": "🌍", "country": "Global"},  # Use -1 here

    
   39: {"name": "Premier League", "flag": "🇬🇧", "country": "England"},
    140: {"name": "La Liga", "flag": "🇪🇸", "country": "Spain"},
    78: {"name": "Bundesliga", "flag": "🇩🇪", "country": "Germany"},
    135: {"name": "Serie A", "flag": "🇮🇹", "country": "Italy"},
    61: {"name": "Ligue 1", "flag": "🇫🇷", "country": "France"},

    88: {"name": "Eredivisie", "flag": "🇳🇱", "country": "Netherlands"},
    144: {"name": "Jupiler Pro League", "flag": "🇧🇪", "country": "Belgium"}, 
    94: {"name": "Primeira Liga", "flag": "🇵🇹", "country": "Portugal"},
   179: {"name": "Scottish Premiership", "flag": "🏴", "country": "Scotland"},
    203: {"name": "Super Lig", "flag": "🇹🇷", "country": "Turkey"},
    207: {"name": "Swiss Super League", "flag": "🇨🇭", "country": "Switzerland"},
    113: {"name": "Allsvenskan", "flag": "🇸🇪", "country": "Sweden"}, 
    119: {"name": "Danish Superliga", "flag": "🇩🇰", "country": "Denmark"},
    103: {"name": "Eliteserien", "flag": "🇳🇴", "country": "Norway"},
    106: {"name": "Ekstraklasa", "flag": "🇵🇱", "country": "Poland"},
   345: {"name": "Czech First League", "flag": "🇨🇿", "country": "Czech Republic"},
   128: {"name": "Austrian Bundesliga", "flag": "🇦🇹", "country": "Austria"},
   332: {"name": "Slovakian Super Liga", "flag": "🇸🇰", "country": "Slovakia"},
   271: {"name": "Nemzeti Bajnokság I", "flag": "🇭🇺", "country": "Hungary"}
} """
