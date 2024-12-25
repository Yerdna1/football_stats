import logging
from datetime import datetime
from config import ALL_LEAGUES, LEAGUE_NAMES

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FormAnalyzer:
    @staticmethod
    def calculate_form_points(results, matches_count=3):
        """Calculate points from last N matches."""
        points = 0
        for result in results[:matches_count]:
            if result == 'W':
                points += 3
            elif result == 'D':
                points += 1
        return points

    @staticmethod
    def analyze_team_form(fixtures, team_id, matches_count=3):
        """Analyze a team's form for the last N matches."""
        team_matches = []
        form = []
        
        # Sort fixtures by date
        sorted_fixtures = sorted(
            fixtures,
            key=lambda x: datetime.strptime(x['fixture']['date'], '%Y-%m-%dT%H:%M:%S%z'),
            reverse=True
        )
        
        # Get completed matches
        for fixture in sorted_fixtures:
            if fixture['fixture']['status']['short'] != 'FT':
                continue

            home_team = fixture['teams']['home']
            away_team = fixture['teams']['away']

            if home_team['id'] == team_id or away_team['id'] == team_id:
                is_home = home_team['id'] == team_id
                team_score = fixture['score']['fulltime']['home'] if is_home else fixture['score']['fulltime']['away']
                opponent_score = fixture['score']['fulltime']['away'] if is_home else fixture['score']['fulltime']['home']
                
                # Determine result
                if team_score > opponent_score:
                    form.append('W')
                elif team_score < opponent_score:
                    form.append('L')
                else:
                    form.append('D')

                team_matches.append(fixture)

                if len(form) >= matches_count:
                    break
        
        # Calculate form points
        form_points = FormAnalyzer.calculate_form_points(form, matches_count)

        return {
            'form': form[:matches_count],
            'points': form_points,
            'matches_analyzed': len(form)
        }


    @staticmethod
    def analyze_all_leagues_standings_vs_form(api, matches_count=3):
        """Compare actual standings with form-based standings across all leagues."""
        form_analysis = []

        logger.info(f"Starting analysis for ALL_LEAGUES at {datetime.now()}...")

        if ALL_LEAGUES in LEAGUE_NAMES:
            logger.info(f"Processing ALL_LEAGUES...")

            # Check if ALL_LEAGUES is in LEAGUE_NAMES
            if ALL_LEAGUES not in LEAGUE_NAMES:
                logger.error("Error: ALL_LEAGUES is not defined in LEAGUE_NAMES")
            else:
                logger.info(f"ALL_LEAGUES found: {LEAGUE_NAMES[ALL_LEAGUES]}")

            for league_id, league_info in LEAGUE_NAMES.items():
                if league_id == ALL_LEAGUES:  # Skip processing ALL_LEAGUES itself
                    continue
            
                try:
                    logger.info(f"Processing league ID: {league_id} - {league_info['name']}")
                    # Fetch standings and fixtures
                    standings = api.fetch_standings(league_id)
                    if not standings or not standings.get('response'):
                        logger.warning(f"No standings data found for league ID: {league_id}")
                        continue

                    standings_data = standings['response'][0]['league']['standings'][0]
                    fixtures = api.fetch_fixtures(league_id)
                    logger.info(f"Fixtures fetched for league ID: {league_id}, Count: {len(fixtures)}")

                    # Analyze each team in the league
                    for team in standings_data:
                        team_id = team['team']['id']
                        form_data = FormAnalyzer.analyze_team_form(fixtures, team_id, matches_count)
                        if form_data['matches_analyzed'] == matches_count:
                            form_analysis.append({
                                'team': team['team']['name'],
                                'league': league_info['name'],
                                'form': ' '.join(form_data['form']),
                                'points': form_data['points'],
                            })

                except Exception as e:
                    logger.error(f"Error processing league {league_id}: {str(e)}", exc_info=True)
                    continue

        logger.info(f"Finished analysis for ALL_LEAGUES at {datetime.now()}, Total Teams Analyzed: {len(form_analysis)}")
        return form_analysis


    @staticmethod
    def get_upcoming_opponents(fixtures, team_id, top_n=5):
        """Get the next N opponents for a team."""
        upcoming_matches = []

        # Sort fixtures by date
        sorted_fixtures = sorted(
            fixtures,
            key=lambda x: datetime.strptime(x['fixture']['date'], '%Y-%m-%dT%H:%M:%S%z')
        )

        # Get upcoming matches
        for fixture in sorted_fixtures:
            if fixture['fixture']['status']['short'] != 'NS':  # Only get not started matches
                continue

            home_team = fixture['teams']['home']
            away_team = fixture['teams']['away']

            if home_team['id'] == team_id or away_team['id'] == team_id:
                opponent = away_team if home_team['id'] == team_id else home_team
                match_date = datetime.strptime(fixture['fixture']['date'], '%Y-%m-%dT%H:%M:%S%z')

                upcoming_matches.append({
                    'date': match_date.strftime('%Y-%m-%d'),
                    'time': match_date.strftime('%H:%M'),
                    'opponent': opponent['name'],
                    'is_home': home_team['id'] == team_id,
                    'venue': fixture['fixture']['venue']['name']
                })

                if len(upcoming_matches) >= top_n:
                    break

        return upcoming_matches
