from datetime import datetime

class WinlessStreakAnalyzer:
    @staticmethod
    def get_last_match(fixtures, team):
        current_time = datetime.now().replace(tzinfo=None)
        team_matches = [f for f in fixtures if 
                       (f['teams']['home']['name'] == team or f['teams']['away']['name'] == team) and
                       f['fixture']['status']['short'] == 'FT' and
                       datetime.strptime(f['fixture']['date'], '%Y-%m-%dT%H:%M:%S%z').replace(tzinfo=None) <= current_time]
        
        if not team_matches:
            return None
            
        last_match = max(team_matches, 
                        key=lambda x: datetime.strptime(x['fixture']['date'], 
                                                      '%Y-%m-%dT%H:%M:%S%z'))
        
        home_team = last_match['teams']['home']['name']
        away_team = last_match['teams']['away']['name']
        home_score = last_match['score']['fulltime']['home']
        away_score = last_match['score']['fulltime']['away']
        match_date = datetime.strptime(last_match['fixture']['date'], 
                                     '%Y-%m-%dT%H:%M:%S%z').strftime('%Y-%m-%d')
        
        return {
            'team': team,
            'result': f"{home_team} vs {away_team}",
            'score': f"{home_score} - {away_score}",
            'date': match_date
        }

    @staticmethod
    def calculate_streaks(fixtures, current_only=False):
        if not fixtures:
            return {}
            
        streaks = {}
        current_streaks = {}
        
        sorted_fixtures = sorted(fixtures, 
                               key=lambda x: datetime.strptime(x['fixture']['date'], 
                                                             '%Y-%m-%dT%H:%M:%S%z'))
        
        for fixture in sorted_fixtures:
            if fixture['fixture']['status']['short'] != 'FT':
                continue
                
            home_team = fixture['teams']['home']['name']
            away_team = fixture['teams']['away']['name']
            home_score = fixture['score']['fulltime']['home']
            away_score = fixture['score']['fulltime']['away']
            
            for team in [home_team, away_team]:
                if team not in current_streaks:
                    current_streaks[team] = 0
                    streaks[team] = 0
            
            if home_score > away_score:
                current_streaks[home_team] = 0
                current_streaks[away_team] += 1
            elif away_score > home_score:
                current_streaks[away_team] = 0
                current_streaks[home_team] += 1
            else:
                current_streaks[home_team] += 1
                current_streaks[away_team] += 1
            
            for team, streak in current_streaks.items():
                if current_only:
                    streaks[team] = current_streaks[team]
                else:
                    streaks[team] = max(streaks[team], streak)
        
        return streaks

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