def create_league_options(leagues):
    options = []
    for league_id, league_info in leagues.items():
        if isinstance(league_info, dict):
            label = f"{league_info['flag']} {league_info['name']} ({league_info['country']})"
            options.append({"value": league_id, "label": label})
        elif isinstance(league_info, str):
            options.append({"value": league_id, "label": league_info})
    return options