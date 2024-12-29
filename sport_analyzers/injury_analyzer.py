import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class InjuriesAnalyzer:
    @staticmethod
    def analyze_team_injuries(response_data):
        """
        Analyze injuries for both teams in a fixture
        
        Args:
            response_data: JSON response from injuries API endpoint
        
        Returns:
            dict: Dictionary containing injuries for home and away teams
        """
        try:
            if not response_data or 'response' not in response_data:
                logger.debug("No injury data provided")
                return {'home': [], 'away': []}

            # Initialize containers for both teams
            injuries = {
                'home': [],
                'away': []
            }
            
            # Track unique team IDs
            teams = set()
            
            # Process each injury entry
            for injury in response_data['response']:
                try:
                    team_id = injury.get('team', {}).get('id')
                    team_name = injury.get('team', {}).get('name')
                    
                    if team_id:
                        teams.add((team_id, team_name))
                        
                    player_data = {
                        'name': injury.get('player', {}).get('name', 'Unknown'),
                        'type': injury.get('player', {}).get('type', 'Unknown'),
                        'reason': injury.get('player', {}).get('reason', 'Unknown'),
                        'team_name': team_name
                    }
                    
                    # First team encountered will be considered home team
                    if len(teams) == 1:
                        injuries['home'].append(player_data)
                    else:
                        injuries['away'].append(player_data)
                except Exception as e:
                    logger.error(f"Error processing injury entry: {str(e)}")
                    continue

            return injuries
        except Exception as e:
            logger.error(f"Error analyzing injuries: {str(e)}")
            return {'home': [], 'away': []}

    @staticmethod
    def display_injuries_report(injuries_data):
        """
        Display a formatted report of team injuries
        
        Args:
            injuries_data: Dictionary containing home and away team injuries
        """
        try:
            print("\n=== MATCH INJURIES REPORT ===\n")
            
            # Display home team injuries
            if injuries_data['home']:
                try:
                    print(f"HOME TEAM: {injuries_data['home'][0]['team_name']}")
                    print("-" * 50)
                    for player in injuries_data['home']:
                        print(f"Player: {player['name']}")
                        print(f"Status: {player['type']}")
                        print(f"Reason: {player['reason']}")
                        print("-" * 30)
                    print()
                except Exception as e:
                    logger.error(f"Error displaying home team injuries: {str(e)}")
                
            # Display away team injuries
            if injuries_data['away']:
                try:
                    print(f"AWAY TEAM: {injuries_data['away'][0]['team_name']}")
                    print("-" * 50)
                    for player in injuries_data['away']:
                        print(f"Player: {player['name']}")
                        print(f"Status: {player['type']}")
                        print(f"Reason: {player['reason']}")
                        print("-" * 30)
                except Exception as e:
                    logger.error(f"Error displaying away team injuries: {str(e)}")
        except Exception as e:
            logger.error(f"Error displaying injuries report: {str(e)}")

# Example usage
if __name__ == "__main__":
    try:
        # Sample response data (you can replace this with actual API response)
        sample_data = {
            "response": [
                {
                    "player": {"name": "D. Costa", "type": "Missing Fixture", "reason": "Broken ankle"},
                    "team": {"id": 157, "name": "Bayern Munich"}
                },
                {
                    "player": {"name": "M. Verratti", "type": "Missing Fixture", "reason": "Illness"},
                    "team": {"id": 85, "name": "Paris Saint Germain"}
                }
            ]
        }
        
        # Analyze injuries
        analyzer = InjuriesAnalyzer()
        injuries = analyzer.analyze_team_injuries(sample_data)
        
        # Display report
        analyzer.display_injuries_report(injuries)
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")