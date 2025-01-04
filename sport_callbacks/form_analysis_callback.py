from datetime import datetime
import json
from venv import logger
from dash.dependencies import Input, Output
import api
from config import ALL_LEAGUES, PERF_DIFF_THRESHOLD
from league_names import LEAGUE_NAMES
from sport_analyzers.form_analyzer import FormAnalyzer
from dash.exceptions import PreventUpdate

# Form Analysis Callbacks
def setup_form_analysis_callbacks(app, api):  
    @app.callback(
        Output('team-selector-dropdown', 'options'),
        [Input('form-analysis-table', 'data')]
    )
    def update_team_dropdown(form_data):
        if not form_data:
            return []
            
        # Get unique teams from form analysis data
        teams = [{'label': row['team'], 'value': row['team']} for row in form_data]
        return teams
    def get_batch_sidelined_history(api, player_ids):
        """Fetch sidelined history for a batch of players (up to 20)"""
        try:
            # Join player IDs with hyphens
            player_param = "-".join(str(pid) for pid in player_ids)
            
            url = f"{api.base_url}/sidelined"
            params = {"player": player_param}
            results = api._batch_request(url, [params])
            sidelined_data = results.get(json.dumps(params), {}).get('response', [])
            
            # Process and format the data
            player_history = {}
            for incident in sidelined_data:
                if incident.get('player', {}).get('id') not in player_ids:
                    continue
                    
                start_date = incident.get('start')
                end_date = incident.get('end')
                incident_type = incident.get('type', 'Unknown')
                
                if start_date and end_date:
                    try:
                        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
                        player_id = incident.get('player', {}).get('id')
                        if player_id not in player_history:
                            player_history[player_id] = []
                        player_history[player_id].append({
                            'type': incident_type,
                            'start': start_date,
                            'end': end_date,
                            'end_date_obj': end_date_obj
                        })
                    except ValueError:
                        continue
            
            # Sort and get last 3 for each player
            for player_id in player_history:
                player_history[player_id] = sorted(
                    player_history[player_id],
                    key=lambda x: x['end_date_obj'],
                    reverse=True
                )[:2]
            
            return player_history
            
        except Exception as e:
            print(f"Error fetching batch sidelined history: {str(e)}")
            return {}
    
    def get_team_injuries_and_history(api, team_id, fixtures):
        """Get current injuries and sidelined history for a team"""
        try:
            injuries_info = []
            
            # Find next match
            sorted_fixtures = sorted(fixtures, 
                                  key=lambda x: x['fixture']['date'],
                                  reverse=True)
            
            next_match = next((f for f in sorted_fixtures 
                             if f['fixture']['status']['short'] not in ['FT', 'AET', 'PEN']), None)

            if not next_match:
                return 'No upcoming matches found'

            # Get current injuries
            fixture_id = next_match['fixture']['id']
            params = {"fixture": fixture_id}
            url = f"{api.base_url}/injuries"
            results = api._batch_request(url, [params])
            injuries_data = results.get(json.dumps(params), {}).get('response', [])
            
            team_injuries = [inj for inj in injuries_data 
                           if inj.get('team', {}).get('id') == team_id]
            
            # Get squad
            url = f"{api.base_url}/players/squads"
            params = {"team": team_id}
            results = api._batch_request(url, [params])
            squad_data = results.get(json.dumps(params), {}).get('response', [])
            
            if not squad_data:
                return 'No squad data available'
                
            squad = squad_data[0].get('players', [])
            
            # Process current injuries
            if team_injuries:
                injuries_info.append("Current Injuries:")
                for inj in team_injuries:
                    player_name = inj.get('player', {}).get('name', 'Unknown')
                    reason = inj.get('player', {}).get('reason', 'Unknown')
                    injuries_info.append(f"{player_name} ({reason})")
                injuries_info.append("")  # Empty line for separation
            
            # Get player IDs from currently injured players
            injured_player_ids = [inj.get('player', {}).get('id') for inj in team_injuries 
                                if inj.get('player', {}).get('id')]
                                
            # Process players in batches of 20
            if injured_player_ids:
                for i in range(0, len(injured_player_ids), 20):
                    batch = injured_player_ids[i:i + 20]
                    sidelined_history = get_batch_sidelined_history(api, batch)
                    
                    if sidelined_history:
                        injuries_info.append("Recent Injury History:")
                        for inj in team_injuries:
                            player_id = inj.get('player', {}).get('id')
                            player_name = inj.get('player', {}).get('name', 'Unknown')
                            if player_id in sidelined_history:
                                injuries_info.append(f"{player_name}:")
                                for incident in sidelined_history[player_id]:
                                    injuries_info.append(
                                        f"- {incident['type']} ({incident['start']} to {incident['end']})"
                                    )
                                injuries_info.append("")  # Empty line between players
            
            return '\n'.join(injuries_info) if injuries_info else 'No injury data available'
            
        except Exception as e:
            print(f"Error getting team injuries and history: {str(e)}")
            return 'Error fetching injury data'

   
      
    @app.callback(
    [Output('form-analysis-table', 'data'),
     Output('upcoming-fixtures-table', 'data')],
    [Input('form-league-dropdown', 'value'),
     Input('form-length-selector', 'value')]
    )
    def update_form_analysis(league_id, form_length):
        logger.info("update_form_analysis callback triggered")
        if not league_id:
            return [], []

        try:
            if league_id == ALL_LEAGUES:
                form_analysis = api.fetch_all_teams(LEAGUE_NAMES, form_length)
            else:
                standings = api.fetch_standings(league_id)
                if not standings or not standings.get('response'):
                    return [], []

                standings_data = standings['response'][0]['league']['standings'][0]
                fixtures = api.fetch_fixtures(league_id)

                form_analysis = []
                for team in standings_data:
                    team_id = team['team']['id']
                    team_name = team['team']['name']
                    actual_points = team['points']

                    form_data = FormAnalyzer.analyze_team_form(fixtures, team_id, form_length)

                    if form_data['matches_analyzed'] == form_length:
                        matches_played = team['all']['played']
                        current_ppg = actual_points / matches_played if matches_played > 0 else 0
                        form_ppg = form_data['points'] / form_length
                        form_vs_actual_diff = form_ppg - current_ppg
                        injury_display = get_team_injuries_and_history(api, team_id, fixtures)
                        league_info = LEAGUE_NAMES.get(league_id, {})
                        performance_diff = round(form_vs_actual_diff, 2)

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
                                'performance_diff': performance_diff,
                                'injured_players': injury_display
                            })

                form_analysis.sort(key=lambda x: abs(x['performance_diff']), reverse=True)

            upcoming_fixtures_data = []
            for team_data in form_analysis[:50]:
                upcoming_matches = FormAnalyzer.get_upcoming_opponents(
                    api.fetch_fixtures(league_id), team_data['team_id'], top_n=1)

                if upcoming_matches:
                    next_match = upcoming_matches[0]
                    try:
                        match_date_here = datetime.strptime(next_match['date'], "%Y-%m-%dT%H:%M:%S%z")
                    except ValueError:
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

            upcoming_fixtures_data.sort(key=lambda x: datetime.strptime(x['date'], "%d-%b-%Y"))

            final_fixtures_data = []
            last_date = None
            for match in upcoming_fixtures_data:
                formatted_date = match['date']
                if formatted_date != last_date:
                    final_fixtures_data.append({
                        'team': f"Date: {formatted_date}",
                        'league': '',
                        'performance_diff': '',
                        'next_opponent': '',
                        'date': formatted_date,
                        'time': '',
                        'venue': '',
                        'caption': True,
                        'style': {'backgroundColor': 'red', 'color': 'white'}
                    })
                    last_date = formatted_date

                final_fixtures_data.append({
                    'team': match['team'],
                    'league': match['league'],
                    'performance_diff': match['performance_diff'],
                    'next_opponent': match['next_opponent'],
                    'date': match['date'],
                    'time': match['time'],
                    'venue': match['venue'],
                    'caption': False,
                    'style': {}
                })

            for fixture in final_fixtures_data:
                if fixture.get('caption', False) or not fixture.get('performance_diff'):
                    fixture['style'] = {'backgroundColor': 'red', 'color': 'white'}

            return form_analysis, final_fixtures_data

        except Exception as e:
            logger.error(f"Error in form analysis: {str(e)}")
            import traceback
            traceback.print_exc()
            return [], []
        
    # form_analysis_callback.py


    @app.callback(
    [Output('basic-stats-container', 'style'),
     Output('advanced-stats-container', 'style'),
     Output('player-stats-table', 'data'),
     Output('advanced-stats-table', 'data')],
    [Input('form-league-dropdown', 'value'),
     Input('stats-type-selector', 'value'),
     Input('team-selector-dropdown', 'value'),
     Input('form-analysis-table', 'data')]
    )
    def update_player_stats(league_id, stats_type, selected_team, form_data):
        print(f"Updating player stats for league {league_id}, selected team: {selected_team}")
        
        # Return immediately if required data is missing
        if not league_id or not form_data:
            return {'display': 'none'}, {'display': 'none'}, [], []
        
        # If no team is selected, do not update the tables
        if not selected_team:
            print("No team selected. Retaining existing table data.")
            raise PreventUpdate  # Prevent the callback from updating the outputs

        try:
            all_player_stats = []
            teams_to_process = [selected_team]
            
            print(f"Teams to process: {teams_to_process}")

            # Process the selected team
            for team_name in teams_to_process:
                try:
                    # Get team ID from standings
                    standings = api.fetch_standings(league_id)
                    standings_data = standings['response'][0]['league']['standings'][0]
                    team_data = next((team for team in standings_data 
                                    if team['team']['name'] == team_name), None)
                    
                    if team_data:
                        team_id = team_data['team']['id']
                        print(f"\nProcessing team: {team_name} (ID: {team_id})")
                        
                        # Fetch squad data
                        url = f"{api.base_url}/players/squads"
                        params = {"team": team_id}
                        results = api._batch_request(url, [params])
                        squad_data = results.get(json.dumps(params), {}).get('response', [])

                        if squad_data and len(squad_data) > 0:
                            # Get player IDs from squad
                            squad = squad_data[0].get('players', [])
                            player_ids = [player.get('id') for player in squad if player.get('id')]
                            print(f"Found {len(player_ids)} players in squad")

                            # Process each player individually
                            for player_id in player_ids:
                                try:
                                    # Get detailed player statistics
                                    url = f"{api.base_url}/players"
                                    params = {
                                        "id": player_id,
                                        "season": "2024",
                                        "league": league_id
                                    }

                                    stats_results = api._batch_request(url, [params])
                                    players_data = stats_results.get(json.dumps(params), {}).get('response', [])

                                    if players_data:
                                        for player_data in players_data:
                                            player = player_data.get('player', {})
                                            stats = player_data.get('statistics', [])
                                            
                                            # Get stats for current team
                                            current_stats = next((s for s in stats 
                                                                if s.get('team', {}).get('id') == team_id), None)

                                            if current_stats:
                                                games = current_stats.get('games', {})
                                                goals = current_stats.get('goals', {})
                                                
                                                player_stats = {
                                                    'name': player.get('name'),
                                                    'age': player.get('age'),
                                                    'position': games.get('position', 'Unknown'),
                                                    'appearances': games.get('appearences', 0),
                                                    'minutes': games.get('minutes', 0),
                                                    'rating': games.get('rating', '0'),
                                                    'goals': goals.get('total', 0),
                                                    'assists': goals.get('assists', 0),
                                                    'yellow_cards': current_stats.get('cards', {}).get('yellow', 0),
                                                    'red_cards': current_stats.get('cards', {}).get('red', 0),
                                                    'shots_total': current_stats.get('shots', {}).get('total', 0),
                                                    'shots_on': current_stats.get('shots', {}).get('on', 0),
                                                    'passes_accuracy': current_stats.get('passes', {}).get('accuracy', 0),
                                                    'passes_key': current_stats.get('passes', {}).get('key', 0),
                                                    'tackles': current_stats.get('tackles', {}).get('total', 0),
                                                    'interceptions': current_stats.get('tackles', {}).get('interceptions', 0),
                                                    'dribbles_success': f"{current_stats.get('dribbles', {}).get('success', 0)}/{current_stats.get('dribbles', {}).get('attempts', 0)}",
                                                    'fouls_drawn': current_stats.get('fouls', {}).get('drawn', 0)
                                                }
                                                print(f"Added stats for player: {player_stats['name']}")
                                                all_player_stats.append(player_stats)
                                                
                                except Exception as e:
                                    print(f"Error processing player {player_id}: {str(e)}")
                                    continue

                except Exception as e:
                    print(f"Error processing team {team_name}: {str(e)}")
                    continue

            # Sort players
            positions = {'Goalkeeper': 1, 'Defender': 2, 'Midfielder': 3, 'Attacker': 4}
            all_player_stats.sort(key=lambda x: (
                positions.get(x.get('position', 'Unknown'), 5),
                -x.get('minutes', 0) if x.get('minutes') is not None else 0
            ))

            print(f"Total players processed: {len(all_player_stats)}")

            # Control visibility
            basic_style = {'display': 'block' if stats_type == 'basic' else 'none'}
            advanced_style = {'display': 'block' if stats_type == 'advanced' else 'none'}

            return basic_style, advanced_style, all_player_stats, all_player_stats

        except Exception as e:
            print(f"Error updating player stats: {str(e)}")
            import traceback
            traceback.print_exc()
            return {'display': 'none'}, {'display': 'none'}, [], []