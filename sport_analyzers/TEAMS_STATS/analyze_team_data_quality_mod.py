from collections import defaultdict
from venv import logger

from sport_analyzers.firebase_analyzer import check_fixture_completeness


def analyze_team_data_quality(fixtures_data):
    """Analyze team data quality from fixtures"""
    logger.info("Starting analyze_team_data_quality function")
    
    team_quality = defaultdict(lambda: {
        'fixtures_count': 0,
        'complete_data': 0,
        'missing_data': 0,
        'missing_statistics': 0,
        'missing_lineups': 0,
        'missing_players': 0,
    })
    
    for fixture in fixtures_data:
        try:
            teams_data = fixture.get('teams', {})
            home_team_id = str(teams_data.get('home', {}).get('id', ''))
            away_team_id = str(teams_data.get('away', {}).get('id', ''))
            
            # Skip if team IDs are missing
            if not home_team_id or not away_team_id:
                logger.warning(f"Skipping fixture with missing team IDs: {fixture.get('id')}")
                continue
            
            # Update fixture count
            team_quality[home_team_id]['fixtures_count'] += 1
            team_quality[away_team_id]['fixtures_count'] += 1
            
            # Check data completeness
            if check_fixture_completeness(fixture):
                team_quality[home_team_id]['complete_data'] += 1
                team_quality[away_team_id]['complete_data'] += 1
            else:
                team_quality[home_team_id]['missing_data'] += 1
                team_quality[away_team_id]['missing_data'] += 1
            
            # Check missing statistics
            if not fixture.get('statistics', []):
                team_quality[home_team_id]['missing_statistics'] += 1
                team_quality[away_team_id]['missing_statistics'] += 1
            
            # Check missing lineups
            if not fixture.get('lineups', []):
                team_quality[home_team_id]['missing_lineups'] += 1
                team_quality[away_team_id]['missing_lineups'] += 1
            
            # Check missing players
            if not fixture.get('players', []):
                team_quality[home_team_id]['missing_players'] += 1
                team_quality[away_team_id]['missing_players'] += 1
        
        except Exception as e:
            logger.error(f"Error processing team data quality: {e}, fixture id: {fixture.get('id')}", exc_info=True)
            continue
    
    logger.info("Finished analyze_team_data_quality function")
    return team_quality