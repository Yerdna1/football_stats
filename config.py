import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

API_KEY = os.getenv('FOOTBALL_API_KEY')  # Instead of hardcoding
BASE_URL = os.getenv('BASE_URL')

ALL_LEAGUES = -1  # Special value for all leagues
PERF_DIFF_THRESHOLD = 0.6

LEAGUE_NAMES = {
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
}