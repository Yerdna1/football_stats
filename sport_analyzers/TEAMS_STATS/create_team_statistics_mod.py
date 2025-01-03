from collections import defaultdict
from venv import logger


def create_team_statistics(fixtures_data):
    """Analyze team statistics from fixtures"""
    logger.info("Starting create_team_statistics function")
    
    team_stats = defaultdict(lambda: {
        'name': '',
        'league': '',
        'matches_played': 0,
        'wins': 0,
        'draws': 0,
        'losses': 0,
        'goals_scored': 0,
        'goals_conceded': 0,
        'clean_sheets': 0,
        'failed_to_score': 0,
        'yellow_cards': 0,
        'red_cards': 0,
        'avg_possession': [],
        'avg_shots': [],
        'avg_passes': [],
        'avg_tackles': [],
        'avg_interceptions': [],
    })
    
    for fixture in fixtures_data:
        try:
            league_name = fixture.get('league', {}).get('name', 'Unknown')
            teams_data = fixture.get('teams', {})
            home_team = teams_data.get('home', {})
            away_team = teams_data.get('away', {})
            home_team_id = str(home_team.get('id', ''))
            away_team_id = str(away_team.get('id', ''))
            
            # Skip if team IDs are missing
            if not home_team_id or not away_team_id:
                logger.warning(f"Skipping fixture with missing team IDs: {fixture.get('id')}")
                continue
            
            # Update team names
            team_stats[home_team_id]['name'] = home_team.get('name', 'Unknown')
            team_stats[away_team_id]['name'] = away_team.get('name', 'Unknown')
            team_stats[home_team_id]['league'] = league_name
            team_stats[away_team_id]['league'] = league_name
            
            # Update matches played
            team_stats[home_team_id]['matches_played'] += 1
            team_stats[away_team_id]['matches_played'] += 1
            
            # Update goals scored and conceded
            goals_data = fixture.get('goals', {})
            home_goals = goals_data.get('home', 0)
            away_goals = goals_data.get('away', 0)
            team_stats[home_team_id]['goals_scored'] += home_goals
            team_stats[home_team_id]['goals_conceded'] += away_goals
            team_stats[away_team_id]['goals_scored'] += away_goals
            team_stats[away_team_id]['goals_conceded'] += home_goals
            
            # Update wins, draws, and losses
            if home_goals > away_goals:
                team_stats[home_team_id]['wins'] += 1
                team_stats[away_team_id]['losses'] += 1
            elif home_goals < away_goals:
                team_stats[away_team_id]['wins'] += 1
                team_stats[home_team_id]['losses'] += 1
            else:
                team_stats[home_team_id]['draws'] += 1
                team_stats[away_team_id]['draws'] += 1
            
            # Update clean sheets and failed to score
            if away_goals == 0:
                team_stats[home_team_id]['clean_sheets'] += 1
            if home_goals == 0:
                team_stats[away_team_id]['clean_sheets'] += 1
            if home_goals == 0:
                team_stats[home_team_id]['failed_to_score'] += 1
            if away_goals == 0:
                team_stats[away_team_id]['failed_to_score'] += 1
            
            # Update cards
            cards_data = fixture.get('cards', {})
            team_stats[home_team_id]['yellow_cards'] += cards_data.get('yellow', {}).get('home', 0)
            team_stats[home_team_id]['red_cards'] += cards_data.get('red', {}).get('home', 0)
            team_stats[away_team_id]['yellow_cards'] += cards_data.get('yellow', {}).get('away', 0)
            team_stats[away_team_id]['red_cards'] += cards_data.get('red', {}).get('away', 0)
            
            # Update statistics (possession, shots, passes, tackles, interceptions)
            stats_data = fixture.get('statistics', [])
            if stats_data:
                home_stats = stats_data[0].get('home', {})
                away_stats = stats_data[0].get('away', {})
                
                team_stats[home_team_id]['avg_possession'].append(home_stats.get('possession', 0))
                team_stats[home_team_id]['avg_shots'].append(home_stats.get('shots', {}).get('total', 0))
                team_stats[home_team_id]['avg_passes'].append(home_stats.get('passes', {}).get('total', 0))
                team_stats[home_team_id]['avg_tackles'].append(home_stats.get('tackles', {}).get('total', 0))
                team_stats[home_team_id]['avg_interceptions'].append(home_stats.get('interceptions', 0))
                
                team_stats[away_team_id]['avg_possession'].append(away_stats.get('possession', 0))
                team_stats[away_team_id]['avg_shots'].append(away_stats.get('shots', {}).get('total', 0))
                team_stats[away_team_id]['avg_passes'].append(away_stats.get('passes', {}).get('total', 0))
                team_stats[away_team_id]['avg_tackles'].append(away_stats.get('tackles', {}).get('total', 0))
                team_stats[away_team_id]['avg_interceptions'].append(away_stats.get('interceptions', 0))
        
        except Exception as e:
            logger.error(f"Error processing team statistics: {e}, fixture id: {fixture.get('id')}", exc_info=True)
            continue
    
    logger.info("Finished create_team_statistics function")
    return team_stats