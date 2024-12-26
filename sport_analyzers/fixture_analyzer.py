from collections import defaultdict
from datetime import datetime
from venv import logger


class FixtureAnalyzer:
    @staticmethod
    def group_fixtures_by_date(fixtures, rows_per_group=20):
        """
        Group fixtures by date and format them for display
        
        Args:
            fixtures: List of fixture data
            rows_per_group: Number of rows to show per date group
            
        Returns:
            dict: Fixtures grouped by date
        """
        try:
            # Group fixtures by date
            grouped_fixtures = defaultdict(list)
            
            for fixture in fixtures:
                try:
                    # Get fixture date
                    fixture_data = fixture.get('fixture', {})
                    date_str = fixture_data.get('date')
                    
                    if not date_str:
                        logger.debug("Missing date in fixture")
                        continue
                        
                    # Parse and format date
                    date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    date_key = date_obj.strftime('%Y-%m-%d')  # Group by day
                    
                    # Get team names
                    teams = fixture.get('teams', {})
                    home_team = teams.get('home', {}).get('name', 'Unknown')
                    away_team = teams.get('away', {}).get('name', 'Unknown')
                    
                    # Get league info
                    league = fixture.get('league', {})
                    league_name = league.get('name', 'Unknown')
                    round_name = league.get('round', '')
                    
                    # Get venue
                    venue = fixture_data.get('venue', {}).get('name', 'TBD')
                    
                    # Get match time
                    match_time = date_obj.strftime('%H:%M')
                    
                    # Get match status
                    status = fixture_data.get('status', {})
                    status_short = status.get('short', 'NS')
                    status_long = status.get('long', 'Not Started')
                    
                    # Get scores if available
                    goals = fixture.get('goals', {})
                    home_goals = goals.get('home', '-')
                    away_goals = goals.get('away', '-')
                    score = f"{home_goals}-{away_goals}" if status_short in ['FT', 'AET', 'PEN'] else '-'
                    
                    fixture_info = {
                        'fixture_id': fixture_data.get('id'),
                        'date': date_key,
                        'time': match_time,
                        'home_team': home_team,
                        'away_team': away_team,
                        'score': score,
                        'status': status_long,
                        'status_short': status_short,
                        'league': league_name,
                        'round': round_name,
                        'venue': venue
                    }
                    
                    grouped_fixtures[date_key].append(fixture_info)
                
                except Exception as e:
                    logger.debug(f"Error processing fixture: {str(e)}")
                    continue
            
            # Sort fixtures within each date
            for date_key in grouped_fixtures:
                grouped_fixtures[date_key].sort(key=lambda x: x['time'])
                # Limit rows if needed
                if len(grouped_fixtures[date_key]) > rows_per_group:
                    grouped_fixtures[date_key] = grouped_fixtures[date_key][:rows_per_group]
            
            # Sort dates
            sorted_dates = sorted(grouped_fixtures.keys())
            
            return {
                date: grouped_fixtures[date]
                for date in sorted_dates
            }
            
        except Exception as e:
            logger.error(f"Error grouping fixtures: {str(e)}")
            return {}

    @staticmethod
    def format_fixture_groups_for_display(grouped_fixtures):
        """
        Format grouped fixtures for display
        
        Args:
            grouped_fixtures: Dictionary of fixtures grouped by date
            
        Returns:
            list: List of tables, one for each date
        """
        formatted_groups = []
        
        for date, fixtures in grouped_fixtures.items():
            try:
                date_obj = datetime.strptime(date, '%Y-%m-%d')
                date_header = date_obj.strftime('%A, %B %d, %Y')
                
                group_data = {
                    'date': date_header,
                    'fixtures': []
                }
                
                for fixture in fixtures:
                    match_data = {
                        'Time': fixture['time'],
                        'League': fixture['league'],
                        'Home': fixture['home_team'],
                        'Score': fixture['score'],
                        'Away': fixture['away_team'],
                        'Status': fixture['status'],
                        'Venue': fixture['venue']
                    }
                    group_data['fixtures'].append(match_data)
                
                formatted_groups.append(group_data)
                
            except Exception as e:
                logger.error(f"Error formatting fixture group for {date}: {str(e)}")
                continue
        
        return formatted_groups
    
    
    
    @staticmethod
    def safe_get_value(data, *keys, default=0):
        """Safely navigate nested dictionaries and handle type conversion"""
        try:
            current = data
            for key in keys:
                if not isinstance(current, dict):
                    logger.debug(f"Not a dict at key {key}: {type(current)}")
                    return default
                current = current.get(key, default)
            
            logger.debug(f"Value before conversion: {current} (type: {type(current)})")
            
            # Handle all possible cases
            if current is None:
                return default
            if isinstance(current, bool):  # Handle boolean values
                return int(current)
            if isinstance(current, str):
                try:
                    return int(float(current.replace(',', '')))  # Handle comma-separated numbers
                except (ValueError, TypeError):
                    return default
            if isinstance(current, (int, float)):
                return int(current)
            
            logger.debug(f"Unhandled type: {type(current)}, returning default")
            return default
            
        except Exception as e:
            logger.debug(f"Error in safe_get_value: {str(e)}")
            return default

    @staticmethod
    def get_player_stats(player_data):
        """Extract player statistics from API response"""
        try:
            player_name = player_data.get('player', {}).get('name', 'Unknown')
            logger.info(f"\n{'='*50}")
            logger.info(f"Processing player: {player_name}")
            
            if not player_data.get('statistics'):
                logger.warning(f"[{player_name}] No statistics array found")
                return None

            # Find the most relevant statistics entry
            stats = None
            most_minutes = -1
            
            logger.info(f"[{player_name}] Checking all statistics entries:")
            for stat in player_data['statistics']:
                logger.info(f"  League: {stat.get('league', {}).get('name')}")
                logger.info(f"  Games: {stat.get('games')}")
                logger.info(f"  Goals: {stat.get('goals')}")
                
                # Get minutes for this entry
                current_minutes = stat.get('games', {}).get('minutes', 0)
                if current_minutes is None:
                    current_minutes = 0
                elif isinstance(current_minutes, str):
                    current_minutes = int(float(current_minutes.replace(',', '')))
                    
                # If this entry has more minutes, use it
                if current_minutes > most_minutes:
                    stats = stat
                    most_minutes = current_minutes
                    logger.info(f"[{player_name}] Found better stats entry with {current_minutes} minutes")
            
            if not stats:
                logger.warning(f"[{player_name}] No valid statistics found")
                return None

            # Process the statistics
            games = stats.get('games', {})
            minutes = games.get('minutes', 0)
            if isinstance(minutes, str):
                minutes = int(float(minutes.replace(',', '')))
            elif minutes is None:
                minutes = 0
                
            appearances = (
                games.get('appearences') or 
                games.get('appearances') or 
                games.get('played', 0)
            )
            if isinstance(appearances, str):
                appearances = int(float(appearances.replace(',', '')))
            elif appearances is None:
                appearances = 0

            # Get goals data
            goals = stats.get('goals', {})
            goals_total = goals.get('total', 0)
            if isinstance(goals_total, str):
                goals_total = int(float(goals_total.replace(',', '')))
            elif goals_total is None:
                goals_total = 0

            assists = goals.get('assists', 0)
            if isinstance(assists, str):
                assists = int(float(assists.replace(',', '')))
            elif assists is None:
                assists = 0

            # Get cards data
            cards = stats.get('cards', {})
            yellow_cards = cards.get('yellow', 0)
            if isinstance(yellow_cards, str):
                yellow_cards = int(float(yellow_cards.replace(',', '')))
            elif yellow_cards is None:
                yellow_cards = 0

            red_cards = cards.get('red', 0)
            if isinstance(red_cards, str):
                red_cards = int(float(red_cards.replace(',', '')))
            elif red_cards is None:
                red_cards = 0

            player_stats = {
                'name': player_name,
                'goals': goals_total,
                'assists': assists,
                'yellow_cards': yellow_cards,
                'red_cards': red_cards,
                'minutes': minutes,
                'matches': appearances,
                'injured': bool(games.get('injured', False)),
                'position': games.get('position', 'Unknown'),
            }
            
            logger.info(f"[{player_name}] Final processed stats: {player_stats}")
            return player_stats
            
        except Exception as e:
            logger.error(f"Error processing player {player_name if 'player_name' in locals() else 'Unknown'}: {str(e)}")
            logger.exception("Full traceback:")
            return None

    @staticmethod
    def analyze_match_statistics(fixture_stats, player_stats, team_stats):
        
        """Analyze upcoming fixture with player and team statistics"""
        try:
            logger.info("Starting match analysis")
            if not player_stats:
                logger.warning("No player statistics available")
                return {
                    'home_team': {'name': 'Data Unavailable', 'players': [], 'team_stats': {}},
                    'away_team': {'name': 'Data Unavailable', 'players': [], 'team_stats': {}},
                    'key_points': ['Statistics temporarily unavailable. Please try again later.']
                }
                
            analysis = {
                'home_team': {'players': [], 'key_points': []},
                'away_team': {'players': [], 'key_points': []},
                'key_points': []
            }
            
            # Process team statistics
            for team_type in ['home', 'away']:
                logger.debug(f"Processing {team_type} team")
                
                team_id = fixture_stats['teams'][team_type]['id']
                team_name = fixture_stats['teams'][team_type]['name']
                
                # Get team stats
                team_data = team_stats.get(team_id, {})
                
                # Process players
                team_players = []
                for p in player_stats:
                    try:
                        if 'statistics' in p and p['statistics']:
                            for stat in p['statistics']:
                                if stat.get('team', {}).get('id') == team_id:
                                    player_stats_processed = FixtureAnalyzer.get_player_stats(p)
                                    if player_stats_processed:
                                        team_players.append(player_stats_processed)
                                    break
                    except Exception as e:
                        logger.error(f"Error processing player stats: {str(e)}")
                        continue
                
                logger.info(f"Processed {len(team_players)} players for {team_name}")
                
                # Sort players
                team_players.sort(key=lambda x: (x.get('goals', 0) or 0, x.get('minutes', 0) or 0), reverse=True)

                
                analysis[f'{team_type}_team'] = {
                    'name': team_name,
                    'players': team_players,
                    'team_stats': team_data
                }
                
                # Add insights about key players and form
                starters = [p for p in team_players if p.get('minutes', 0) > 0]
                if starters:
                    scorers = [p for p in starters if p.get('goals', 0) > 0]
                    if scorers:
                        scorers_info = ", ".join([f"{p['name']} ({p['goals']} goals)" 
                                                for p in sorted(scorers, 
                                                            key=lambda x: x['goals'], 
                                                            reverse=True)[:3]])
                        analysis['key_points'].append(f"{team_name} top scorers: {scorers_info}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in analyze_match_statistics: {str(e)}")
            logger.exception("Full traceback:")
            return {
                'home_team': {'name': 'Error', 'players': [], 'team_stats': {}},
                'away_team': {'name': 'Error', 'players': [], 'team_stats': {}},
                'key_points': ['Error analyzing match statistics']
            }

