from datetime import datetime


class TeamAnalyzer:
    @staticmethod
    def analyze_team_results(fixtures, team_id):
        if not fixtures:
            return []
            
        results = []
        for fixture in sorted(fixtures, 
                            key=lambda x: datetime.strptime(x['fixture']['date'], 
                                                          '%Y-%m-%dT%H:%M:%S%z')):
            if fixture['fixture']['status']['short'] != 'FT':
                continue
                
            home_team = fixture['teams']['home']
            away_team = fixture['teams']['away']
            home_score = fixture['score']['fulltime']['home']
            away_score = fixture['score']['fulltime']['away']
            
            is_home = home_team['id'] == team_id
            team_score = home_score if is_home else away_score
            opponent_score = away_score if is_home else home_score
            opponent_name = away_team['name'] if is_home else home_team['name']
            
            if team_score > opponent_score:
                result = {'symbol': 'W', 'color': 'green'}
            elif team_score < opponent_score:
                result = {'symbol': 'L', 'color': 'red'}
            else:
                result = {'symbol': 'D', 'color': '#FFD700'}
                
            results.append({
                'date': datetime.strptime(fixture['fixture']['date'], 
                                        '%Y-%m-%dT%H:%M:%S%z').strftime('%Y-%m-%d'),
                'opponent': opponent_name,
                'score': f"{team_score} - {opponent_score}",
                'result': result
            })
            
        return results

    @staticmethod
    def find_scoreless_teams(fixtures, min_games=3):
        team_stats = {}
        
        for fixture in fixtures:
            if fixture['fixture']['status']['short'] != 'FT':
                continue
                
            for team_type in ['home', 'away']:
                team = fixture['teams'][team_type]
                score = fixture['score']['fulltime'][team_type]
                
                if team['id'] not in team_stats:
                    team_stats[team['id']] = {
                        'name': team['name'],
                        'games': 0,
                        'scoreless_streak': 0,
                        'current_streak': 0
                    }
                
                stats = team_stats[team['id']]
                stats['games'] += 1
                
                if score == 0:
                    stats['current_streak'] += 1
                    stats['scoreless_streak'] = max(stats['scoreless_streak'], 
                                                  stats['current_streak'])
                else:
                    stats['current_streak'] = 0
        
        return [{'team': stats['name'], 
                'scoreless_games': stats['scoreless_streak']}
               for stats in team_stats.values()
               if stats['scoreless_streak'] >= min_games]

