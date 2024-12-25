from dash.dependencies import Input, Output
from config import ALL_LEAGUES
from sport_analyzers import TeamAnalyzer  
  
def setup_team_analysis_callbacks(app, api):  
    @app.callback(
    [Output('team-dropdown', 'options'),
     Output('team-dropdown', 'value')],
    Input('team-league-dropdown', 'value')
        )
    def update_teams(league_id):
            if not league_id or league_id == ALL_LEAGUES:
                return [], None
            
            standings = api.fetch_standings(league_id)
            if not standings or not standings.get('response'):
                return [], None
                    
            teams = standings['response'][0]['league']['standings'][0]
            options = [{'label': team['team']['name'], 
                        'value': team['team']['id']} 
                    for team in teams]
            
            # Sort teams alphabetically by name
           #  sorted_options = sorted(options, key=lambda x: x['label'])
            
            # Reset the selected value when league changes
            return sorted(options, key=lambda x: x['label']), None

        # Callback to update team analysis results
    @app.callback(
            [Output('team-results-table', 'data'),
             Output('team-results-table', 'style_data_conditional'),
             Output('scoreless-teams-table', 'data')],
            [Input('team-league-dropdown', 'value'),
             Input('team-dropdown', 'value')]
        )
    def update_team_analysis(league_id, team_id):
            if not team_id:
                return [], [], []
                
            fixtures = api.fetch_fixtures(league_id, team_id=team_id)
            results = TeamAnalyzer.analyze_team_results(fixtures, team_id)
            
            # Prepare results table data
            table_data = []
            style_conditions = [{
                'if': {'column_id': 'result_display'},
                'fontWeight': 'bold'
            }]
            
            for res in results:
                result = res['result']
                table_data.append({
                    'date': res['date'],
                    'opponent': res['opponent'],
                    'score': res['score'],
                    'result_display': result['symbol']
                })
                style_conditions.append({
                    'if': {'column_id': 'result_display',
                           'filter_query': f'{{result_display}} = "{result["symbol"]}"'},
                    'color': result['color']
                })
            
            # Get scoreless teams
            scoreless = TeamAnalyzer.find_scoreless_teams(fixtures)
            
            return table_data, style_conditions, scoreless