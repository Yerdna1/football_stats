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

