from datetime import datetime
from dash.dependencies import Input, Output
from config import ALL_LEAGUES, LEAGUE_NAMES, PERF_DIFF_THRESHOLD
from sport_analyzers.form_analyzer import FormAnalyzer

# Form Analysis Callbacks
def setup_form_analysis_callbacks(app, api):    
    @app.callback(
        [Output('form-analysis-table', 'data'),
         Output('upcoming-fixtures-table', 'data')],
        [Input('form-league-dropdown', 'value'),
         Input('form-length-selector', 'value')]
    )
    def update_form_analysis(league_id, form_length):
        if not league_id:
            return [], []

        try:
            if league_id == ALL_LEAGUES:
                form_analysis = api.fetch_all_teams(LEAGUE_NAMES, form_length)

            else:
                # Fetch standings and fixtures for a single league
                standings = api.fetch_standings(league_id)
                if not standings or not standings.get('response'):
                    return [], []

                standings_data = standings['response'][0]['league']['standings'][0]
                fixtures = api.fetch_fixtures(league_id)

                # Analyze form vs standings
                form_analysis = []
                for team in standings_data:
                    team_id = team['team']['id']
                    team_name = team['team']['name']
                    actual_points = team['points']

                    # Get form analysis
                    form_data = FormAnalyzer.analyze_team_form(fixtures, team_id, form_length)

                    if form_data['matches_analyzed'] == form_length:
                        matches_played = team['all']['played']
                        current_ppg = actual_points / matches_played if matches_played > 0 else 0
                        form_ppg = form_data['points'] / form_length
                        form_vs_actual_diff = form_ppg - current_ppg

                        league_info = LEAGUE_NAMES.get(league_id, {})
                        performance_diff = round(form_vs_actual_diff, 2)
                        # Only include teams where the absolute performance_diff > PERF_DIFF_THRESHOLD
                        if abs(performance_diff) > PERF_DIFF_THRESHOLD:
                            form_analysis.append({
                                'team_id': team_id,
                                'team': team_name,
                                'league': f"{league_info.get('flag', '')} {league_info.get('name', '')}",
                                'current_position': team['rank'],
                                'current_points': actual_points,
                                'current_ppg': round(current_ppg, 2),
                                'form': ' '.join(form_data['form']),
                                'form_points': form_data['points'],
                                'form_ppg': round(form_ppg, 2),
                                'performance_diff': performance_diff
                            })

                form_analysis.sort(key=lambda x: abs(x['performance_diff']), reverse=True)

            # Get upcoming fixtures for top 50 teams
            upcoming_fixtures_data = []
            for team_data in form_analysis[:50]:
                upcoming_matches = FormAnalyzer.get_upcoming_opponents(
                    api.fetch_fixtures(league_id), team_data['team_id'], top_n=1)

                if upcoming_matches:
                    next_match = upcoming_matches[0]

                    # Check if the date is in the correct format; parse and format it
                    try:
                        # Try to parse the date as '%Y-%m-%dT%H:%M:%S%z' first (standard API format)
                        match_date_here = datetime.strptime(next_match['date'], "%Y-%m-%dT%H:%M:%S%z")
                    except ValueError:
                        # If it fails, try parsing it as '%d-%b-%Y' (e.g., '26-Dec-2024')
                        match_date_here = datetime.strptime(next_match['date'], "%d-%b-%Y")

                    formatted_date_here = match_date_here.strftime("%d-%b-%Y")

                    upcoming_fixtures_data.append({
                        'team': team_data['team'],
                        'league': team_data['league'],
                        'performance_diff': team_data['performance_diff'],
                        'next_opponent': next_match['opponent'],
                        'date': formatted_date_here,
                        'time': next_match['time'],
                        'venue': next_match['venue']
                    })

            # Sort upcoming fixtures by the original date format
            upcoming_fixtures_data.sort(key=lambda x: datetime.strptime(x['date'], "%d-%b-%Y"))

            # Add caption rows with red background before each new date
            final_fixtures_data = []
            last_date = None
            for match in upcoming_fixtures_data:
                # Use the formatted date directly
                formatted_date = match['date']
                if formatted_date != last_date:
                    # Add a caption row for the new date
                    final_fixtures_data.append({
                        'team': f"Date: {formatted_date}",
                        'league': '',
                        'performance_diff': '',
                        'next_opponent': '',
                        'date': formatted_date,
                        'time': '',
                        'venue': '',
                        'caption': True,  # Used to identify the row as a caption
                        'style': {'backgroundColor': 'red', 'color': 'white'}  # Apply red background directly

                    })
                    last_date = formatted_date

                # Add the actual fixture row
                final_fixtures_data.append({
                    'team': match['team'],
                    'league': match['league'],
                    'performance_diff': match['performance_diff'],
                    'next_opponent': match['next_opponent'],
                    'date': match['date'],
                    'time': match['time'],
                    'venue': match['venue'],
                    'caption': False, # Regular fixture row
                    'style': {}  # Default style for regular rows
                })

            # Now, format the rows that are captions or have empty performance_diff
            for fixture in final_fixtures_data:
                if fixture.get('caption', False) or not fixture.get('performance_diff'):
                    fixture['style'] = {'backgroundColor': 'red', 'color': 'white'}

            return form_analysis, final_fixtures_data

        except Exception as e:
            print(f"Error in form analysis: {str(e)}")
            import traceback
            traceback.print_exc()
            return [], []
