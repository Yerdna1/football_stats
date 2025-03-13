# League names dictionary with flags and countries

ALL_LEAGUES = -1  # Special value for all leagues

LEAGUE_NAMES = {
    ALL_LEAGUES: {"name": "All Leagues", "flag": "🌍", "country": "Global"},  # Use -1 here
    
    # Top 5 European Leagues
    39: {"name": "Premier League", "flag": "🇬🇧", "country": "England"},
    140: {"name": "La Liga", "flag": "🇪🇸", "country": "Spain"},
    78: {"name": "Bundesliga", "flag": "🇩🇪", "country": "Germany"},
    135: {"name": "Serie A", "flag": "🇮🇹", "country": "Italy"},
    61: {"name": "Ligue 1", "flag": "🇫🇷", "country": "France"},

    # Other European Leagues
    88: {"name": "Eredivisie", "flag": "🇳🇱", "country": "Netherlands"},
    144: {"name": "Jupiler Pro League", "flag": "🇧🇪", "country": "Belgium"}, 
    94: {"name": "Primeira Liga", "flag": "🇵🇹", "country": "Portugal"},
    179: {"name": "Scottish Premiership", "flag": "🏴󠁧󠁢󠁳󠁣󠁴󠁿", "country": "Scotland"},
    203: {"name": "Super Lig", "flag": "🇹🇷", "country": "Turkey"},
    207: {"name": "Swiss Super League", "flag": "🇨🇭", "country": "Switzerland"},
    113: {"name": "Allsvenskan", "flag": "🇸🇪", "country": "Sweden"}, 
    119: {"name": "Danish Superliga", "flag": "🇩🇰", "country": "Denmark"},
    103: {"name": "Eliteserien", "flag": "🇳🇴", "country": "Norway"},
    106: {"name": "Ekstraklasa", "flag": "🇵🇱", "country": "Poland"},
    345: {"name": "Czech First League", "flag": "🇨🇿", "country": "Czech Republic"},
    128: {"name": "Austrian Bundesliga", "flag": "🇦🇹", "country": "Austria"},
    332: {"name": "Slovakian Super Liga", "flag": "🇸🇰", "country": "Slovakia"},
    271: {"name": "Nemzeti Bajnokság I", "flag": "🇭🇺", "country": "Hungary"},
    
    # Second Divisions in Europe
    40: {"name": "Championship", "flag": "🇬🇧", "country": "England"},
    141: {"name": "La Liga 2", "flag": "🇪🇸", "country": "Spain"},
    79: {"name": "2. Bundesliga", "flag": "🇩🇪", "country": "Germany"},
    136: {"name": "Serie B", "flag": "🇮🇹", "country": "Italy"},
    62: {"name": "Ligue 2", "flag": "🇫🇷", "country": "France"},
    
    # South American Leagues
    71: {"name": "Serie A", "flag": "🇧🇷", "country": "Brazil"},
    128: {"name": "Primera División", "flag": "🇦🇷", "country": "Argentina"},
    239: {"name": "Primera División", "flag": "🇺🇾", "country": "Uruguay"},
    350: {"name": "Primera División", "flag": "🇨🇱", "country": "Chile"},
    239: {"name": "Primera División", "flag": "🇵🇾", "country": "Paraguay"},
    
    # North American Leagues
    253: {"name": "MLS", "flag": "🇺🇸", "country": "USA"},
    262: {"name": "Liga MX", "flag": "🇲🇽", "country": "Mexico"},
    
    # Asian Leagues
    98: {"name": "J1 League", "flag": "🇯🇵", "country": "Japan"},
    292: {"name": "K League 1", "flag": "🇰🇷", "country": "South Korea"},
    169: {"name": "Chinese Super League", "flag": "🇨🇳", "country": "China"},
    305: {"name": "Saudi Pro League", "flag": "🇸🇦", "country": "Saudi Arabia"},
    307: {"name": "UAE Pro League", "flag": "🇦🇪", "country": "UAE"},
    
    # Australian League
    188: {"name": "A-League", "flag": "🇦🇺", "country": "Australia"},
    
    # African Leagues
    323: {"name": "Premier Soccer League", "flag": "🇿🇦", "country": "South Africa"},
    200: {"name": "Egyptian Premier League", "flag": "🇪🇬", "country": "Egypt"},
    202: {"name": "Botola Pro", "flag": "🇲🇦", "country": "Morocco"},
    
    # Additional European Leagues
    282: {"name": "Superliga", "flag": "🇷🇸", "country": "Serbia"},
    283: {"name": "HNL", "flag": "🇭🇷", "country": "Croatia"},
    266: {"name": "Super League", "flag": "🇬🇷", "country": "Greece"},
    238: {"name": "Premier League", "flag": "🇺🇦", "country": "Ukraine"},
    235: {"name": "Premier League", "flag": "🇷🇺", "country": "Russia"},
    210: {"name": "Veikkausliiga", "flag": "🇫🇮", "country": "Finland"},
    233: {"name": "Liga I", "flag": "🇷🇴", "country": "Romania"},
    244: {"name": "First Professional League", "flag": "🇧🇬", "country": "Bulgaria"},
    
    # Cup Competitions
    45: {"name": "FA Cup", "flag": "🇬🇧", "country": "England"},
    48: {"name": "EFL Cup", "flag": "🇬🇧", "country": "England"},
    143: {"name": "Copa del Rey", "flag": "🇪🇸", "country": "Spain"},
    81: {"name": "DFB Pokal", "flag": "🇩🇪", "country": "Germany"},
    137: {"name": "Coppa Italia", "flag": "🇮🇹", "country": "Italy"},
    66: {"name": "Coupe de France", "flag": "🇫🇷", "country": "France"},
    
    # International Competitions
    2: {"name": "UEFA Champions League", "flag": "🇪🇺", "country": "Europe"},
    3: {"name": "UEFA Europa League", "flag": "🇪🇺", "country": "Europe"},
    848: {"name": "UEFA Conference League", "flag": "🇪🇺", "country": "Europe"},
    1: {"name": "World Cup", "flag": "🌍", "country": "International"},
    5: {"name": "UEFA Euro", "flag": "🇪🇺", "country": "Europe"},
    15: {"name": "Copa America", "flag": "🌎", "country": "South America"},
    10: {"name": "AFC Asian Cup", "flag": "🌏", "country": "Asia"}
}

def get_league_display_name(league_id):
    """Get formatted league name with flag for display"""
    if league_id == ALL_LEAGUES:
        return "All Leagues"
    
    league_info = LEAGUE_NAMES.get(league_id, {})
    if league_info:
        return f"{league_info['flag']} {league_info['name']} ({league_info['country']})"
    return "Selected League"

def get_league_options():
    """Get league options for dropdown menus"""
    options = []
    
    # Add All Leagues option first
    options.append({
        "id": ALL_LEAGUES,
        "text": f"{LEAGUE_NAMES[ALL_LEAGUES]['flag']} {LEAGUE_NAMES[ALL_LEAGUES]['name']}"
    })
    
    # Group leagues by country
    leagues_by_country = {}
    for league_id, league_info in LEAGUE_NAMES.items():
        if league_id == ALL_LEAGUES:
            continue
            
        country = league_info["country"]
        if country not in leagues_by_country:
            leagues_by_country[country] = []
            
        leagues_by_country[country].append({
            "id": league_id,
            "text": f"{league_info['flag']} {league_info['name']}"
        })
    
    # Add leagues grouped by country
    for country, leagues in sorted(leagues_by_country.items()):
        for league in leagues:
            options.append(league)
    
    return options
