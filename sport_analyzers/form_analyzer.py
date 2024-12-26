from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class FormAnalyzer:
    @staticmethod
    def analyze_team_form(fixtures, team_id, matches_count=3):
        """
        Analyze a team's recent form with enhanced debugging and null safety
        """
        logger.debug(f"Starting form analysis for team {team_id}")
        
        # Validate input parameters
        if not fixtures:
            logger.debug("No fixtures provided")
            return FormAnalyzer._get_default_form(matches_count)
        if not team_id:
            logger.debug("No team_id provided")
            return FormAnalyzer._get_default_form(matches_count)

        try:
            # Debug log the fixtures
            logger.debug(f"Processing {len(fixtures)} fixtures")
            
            # Sort and filter fixtures
            valid_fixtures = []
            for fixture in fixtures:
                try:
                    if not isinstance(fixture, dict):
                        logger.debug(f"Invalid fixture format: {type(fixture)}")
                        continue
                        
                    fixture_date = fixture.get('fixture', {}).get('date')
                    if not fixture_date:
                        logger.debug("Fixture missing date")
                        continue
                        
                    valid_fixtures.append(fixture)
                except Exception as e:
                    logger.debug(f"Error processing fixture: {str(e)}")
                    continue

            sorted_fixtures = sorted(
                valid_fixtures,
                key=lambda x: x['fixture']['date'],
                reverse=True
            )

            # Process matches
            form = []
            points = 0
            goals_for = 0
            goals_against = 0
            matches_analyzed = 0

            for match in sorted_fixtures:
                try:
                    # Skip if not finished
                    status = match.get('fixture', {}).get('status', {}).get('short')
                    if status != 'FT':
                        logger.debug(f"Skipping match with status: {status}")
                        continue

                    # Get team data safely
                    teams = match.get('teams', {})
                    home_team = teams.get('home', {})
                    away_team = teams.get('away', {})
                    
                    if not home_team or not away_team:
                        logger.debug("Missing team data in match")
                        continue
                        
                    # Validate team identification
                    if team_id not in [home_team.get('id'), away_team.get('id')]:
                        logger.debug(f"Match does not involve team {team_id}")
                        continue
                        
                    logger.debug(f"""
                        Match teams:
                        Home: {home_team.get('name')} (ID: {home_team.get('id')})
                        Away: {away_team.get('name')} (ID: {away_team.get('id')})
                    """)

                    # Get goals safely
                    goals = match.get('goals', {})
                    home_goals = goals.get('home')
                    away_goals = goals.get('away')
                    
                    if home_goals is None or away_goals is None:
                        logger.debug("Missing goals data in match")
                        continue

                    # Convert goals to int with explicit error handling
                    try:
                        home_goals = int(home_goals)
                        away_goals = int(away_goals)
                    except (ValueError, TypeError) as e:
                        logger.debug(f"Error converting goals to int: {str(e)}")
                        continue

                    # Determine if team was home or away
                    is_home = home_team.get('id') == team_id
                    team_goals = home_goals if is_home else away_goals
                    opponent_goals = away_goals if is_home else home_goals
                    opponent_name = (away_team if is_home else home_team).get('name', 'Unknown')

                    # Debug logging for match analysis
                    logger.debug(f"""
                        Analyzing match:
                        Team: {team_id} {'(Home)' if is_home else '(Away)'}
                        Opponent: {opponent_name}
                        Score: {home_goals}-{away_goals}
                        Team goals: {team_goals}
                        Opponent goals: {opponent_goals}
                        Teams data: {teams}
                        Match date: {match.get('fixture', {}).get('date')}
                    """)

                    # Calculate result
                    if team_goals > opponent_goals:
                        form.append('W')
                        points += 3
                        logger.debug(f"Result: Win against {opponent_name}")
                    elif team_goals < opponent_goals:
                        form.append('L')
                        logger.debug(f"Result: Loss against {opponent_name}")
                    else:
                        form.append('D')
                        points += 1
                        logger.debug(f"Result: Draw against {opponent_name}")

                    goals_for += team_goals
                    goals_against += opponent_goals
                    matches_analyzed += 1

                    if matches_analyzed >= matches_count:
                        break

                except Exception as e:
                    logger.debug(f"Error analyzing match: {str(e)}")
                    continue

            # Pad form if needed
            while len(form) < matches_count:
                form.append('U')

            result = {
                'form': form,
                'points': points,
                'matches_analyzed': matches_analyzed,
                'goals_for': goals_for,
                'goals_against': goals_against
            }
            
            logger.debug(f"Form analysis result: {result}")
            return result

        except Exception as e:
            logger.error(f"Error in form analysis: {str(e)}")
            return FormAnalyzer._get_default_form(matches_count)

    @staticmethod
    def _get_default_form(matches_count):
        """Get default form data"""
        return {
            'form': ['U'] * matches_count,
            'points': 0,
            'matches_analyzed': 0,
            'goals_for': 0,
            'goals_against': 0
        }
        
    @staticmethod
    def get_upcoming_opponents(fixtures, team_id, top_n=5):
        """
        Get upcoming opponents for a team from fixtures
        
        Args:
            fixtures: List of fixture data
            team_id: ID of the team to analyze
            top_n: Number of upcoming matches to analyze
            
        Returns:
            list: List of upcoming opponent details
        """
        logger.debug(f"Getting upcoming opponents for team {team_id}, top_n={top_n}")
        
        if not fixtures or not team_id:
            logger.debug("No fixtures or team_id provided")
            return []

        try:
            # Filter and sort upcoming matches
            upcoming = []
            for fixture in fixtures:
                try:
                    if not isinstance(fixture, dict):
                        continue
                        
                    # Get fixture status
                    status = fixture.get('fixture', {}).get('status', {}).get('short')
                    if status in ['FT', 'AET', 'PEN']:  # Skip finished matches
                        continue
                        
                    # Get teams data
                    teams = fixture.get('teams', {})
                    home_team = teams.get('home', {})
                    away_team = teams.get('away', {})
                    
                    if not home_team or not away_team:
                        continue
                        
                    # Check if our team is involved
                    if team_id not in [home_team.get('id'), away_team.get('id')]:
                        continue
                        
                    # Get opponent details
                    is_home = home_team.get('id') == team_id
                    opponent = away_team if is_home else home_team
                    
                    # Get fixture date
                    fixture_date = fixture.get('fixture', {}).get('date')
                    if not fixture_date:
                        continue
                        
                    # Extract time from the fixture date
                    try:
                        fixture_datetime = datetime.fromisoformat(fixture_date.replace('Z', '+00:00'))
                        match_time = fixture_datetime.strftime('%H:%M')
                    except Exception as e:
                        logger.debug(f"Error parsing fixture date: {str(e)}")
                        match_time = "TBD"
                        
                    match_details = {
                        'opponent_id': opponent.get('id'),
                        'opponent': opponent.get('name', 'Unknown'),
                        'is_home': is_home,
                        'date': fixture_date,
                        'time': match_time,
                        'fixture_id': fixture.get('fixture', {}).get('id'),
                        'league': fixture.get('league', {}).get('name', 'Unknown'),
                        'round': fixture.get('league', {}).get('round', 'Unknown'),
                        'venue': fixture.get('fixture', {}).get('venue', {}).get('name', 'Unknown'),
                        'timestamp': fixture.get('fixture', {}).get('timestamp', 0),
                        'status': fixture.get('fixture', {}).get('status', {}).get('long', 'Not Started')
                    }
                    
                    upcoming.append((fixture_date, match_details))
                    
                except Exception as e:
                    logger.debug(f"Error processing fixture: {str(e)}")
                    continue
                    
            # Sort by date and get the next matches
            upcoming.sort(key=lambda x: x[0])
            return [match[1] for match in upcoming[:top_n]]
            
        except Exception as e:
            logger.error(f"Error getting upcoming opponents: {str(e)}")
            return []