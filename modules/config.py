# API Configuration
API_KEY = "2061b15078fc8e299dd268fb5a066f34"
BASE_URL = "https://v3.football.api-sports.io"

# Special value for all leagues
ALL_LEAGUES = -1

# Performance difference threshold
PERF_DIFF_THRESHOLD = 0.75

# Prediction thresholds
PREDICTION_THRESHOLD_LEVEL1 = 0.75  # For WIN/LOSS
PREDICTION_THRESHOLD_LEVEL2 = 1.05  # For BIG WIN/BIG LOSS

# Theme configuration
THEMES = {
    "blue": {
        "primary": "#1E88E5",
        "secondary": "#64B5F6",
        "accent": "#0D47A1",
        "text": "#FFFFFF",
        "background": "#F5F5F5",
        "card": "#FFFFFF",
        "border": "#E0E0E0"
    },
    "green": {
        "primary": "#43A047",
        "secondary": "#81C784",
        "accent": "#2E7D32",
        "text": "#FFFFFF",
        "background": "#F5F5F5",
        "card": "#FFFFFF",
        "border": "#E0E0E0"
    },
    "purple": {
        "primary": "#8E24AA",
        "secondary": "#BA68C8",
        "accent": "#6A1B9A",
        "text": "#FFFFFF",
        "background": "#F5F5F5",
        "card": "#FFFFFF",
        "border": "#E0E0E0"
    },
    "red": {
        "primary": "#E53935",
        "secondary": "#EF5350",
        "accent": "#C62828",
        "text": "#FFFFFF",
        "background": "#F5F5F5",
        "card": "#FFFFFF",
        "border": "#E0E0E0"
    },
    "dark": {
        "primary": "#424242",
        "secondary": "#757575",
        "accent": "#212121",
        "text": "#FFFFFF",
        "background": "#303030",
        "card": "#424242",
        "border": "#616161"
    }
}

# Default settings
DEFAULT_SETTINGS = {
    "appearance_mode": "System",
    "color_theme": "blue",
    "form_length": 5,
    "threshold": PERF_DIFF_THRESHOLD,
    "auto_refresh": False,
    "refresh_interval": 30,
    "leagues": [39],  # Premier League
    "prediction_threshold_level1": PREDICTION_THRESHOLD_LEVEL1,
    "prediction_threshold_level2": PREDICTION_THRESHOLD_LEVEL2,
    "font_size": 50  # Default font size for tables and detail windows
}

# Football data fetcher class
class FootballDataFetcher:
    def __init__(self, api_key=API_KEY, base_url=BASE_URL):
        self.api_key = api_key
        self.base_url = base_url
        
    def find_active_leagues(self):
        """Find active leagues for the current season"""
        # This is a placeholder implementation
        return []
        
def generate_league_names_dict(leagues):
    """Generate a Python dictionary of league names"""
    # This is a placeholder implementation
    return "LEAGUE_NAMES = {}"
