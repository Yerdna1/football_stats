import api
from config import ALL_LEAGUES, LEAGUE_NAMES


class LeagueAnalyzer:
    @staticmethod
    def calculate_league_stats(fixtures):
        if not fixtures:
            return {
                'avg_goals': 0,
                'avg_yellows': 0,
                'avg_reds': 0,
                'common_results': []
            }
            
        total_matches = 0
        total_goals = 0
        total_yellows = 0
        total_reds = 0
        results_count = {}
        
        for fixture in fixtures:
            if fixture['fixture']['status']['short'] != 'FT':
                continue
                
            total_matches += 1
            
            # Calculate goals
            home_goals = fixture['score']['fulltime']['home']
            away_goals = fixture['score']['fulltime']['away']
            total_goals += home_goals + away_goals
            
            # Count result frequency
            result_key = f"{home_goals}-{away_goals}"
            results_count[result_key] = results_count.get(result_key, 0) + 1
            
            # Calculate cards
            if 'statistics' in fixture:
                for team_stats in fixture.get('statistics', []):
                    for stat in team_stats:
                        if stat['type'] == 'Yellow Cards':
                            total_yellows += int(stat['value'] or 0)
                        elif stat['type'] == 'Red Cards':
                            total_reds += int(stat['value'] or 0)
        
        # Calculate averages
        avg_goals = round(total_goals / total_matches, 2) if total_matches > 0 else 0
        avg_yellows = round(total_yellows / total_matches, 2) if total_matches > 0 else 0
        avg_reds = round(total_reds / total_matches, 2) if total_matches > 0 else 0
        
        # Get most common results
        sorted_results = sorted(results_count.items(), 
                              key=lambda x: (-x[1], x[0]))  # Sort by count desc, then result
        common_results = [
            {
                'result': result,
                'count': count,
                'percentage': round((count / total_matches) * 100, 1)
            }
            for result, count in sorted_results[:10]  # Top 10 most common results
        ]
        
        return {
            'avg_goals': avg_goals,
            'avg_yellows': avg_yellows,
            'avg_reds': avg_reds,
            'common_results': common_results
        }

    @staticmethod
    def get_all_leagues_fixtures(api):
        """Fetch fixtures for all leagues"""
        all_fixtures = []
        for league_id, league_info in LEAGUE_NAMES.items():
            if isinstance(league_id, int) and league_id != ALL_LEAGUES:  # Skip ALL_LEAGUES entry
                try:
                    fixtures = api.fetch_fixtures(league_id)
                    all_fixtures.extend(fixtures)
                except Exception as e:
                    print(f"Error fetching fixtures for league {league_id}: {str(e)}")
                    continue
        return all_fixtures
    @staticmethod
    def calculate_all_leagues_goals():
        """Calculate goal statistics for all leagues"""
        league_stats = []
        
        for league_id, league_info in LEAGUE_NAMES.items():
            if isinstance(league_id, int):  # Skip ALL_LEAGUES entry
                try:
                    fixtures = api.fetch_fixtures(league_id)
                    total_goals = 0
                    total_matches = 0
                    
                    for fixture in fixtures:
                        if fixture['fixture']['status']['short'] == 'FT':
                            total_matches += 1
                            total_goals += (fixture['score']['fulltime']['home'] + 
                                          fixture['score']['fulltime']['away'])
                    
                    if total_matches > 0:
                        avg_goals = round(total_goals / total_matches, 2)
                        league_stats.append({
                            'league': f"{league_info['flag']} {league_info['name']}",
                            'avg_goals': avg_goals,
                            'total_goals': total_goals,
                            'matches': total_matches
                        })
                except Exception as e:
                    print(f"Error processing league {league_id}: {str(e)}")
                    continue
        
        return sorted(league_stats, key=lambda x: x['avg_goals'], reverse=True)

    @staticmethod
    def calculate_league_stats(fixtures):
        if not fixtures:
            return {
                'avg_goals': 0,
                'avg_yellows': 0,
                'avg_reds': 0,
                'common_results': []
            }
            
        total_matches = 0
        total_goals = 0
        total_yellows = 0
        total_reds = 0
        results_count = {}
        
        for fixture in fixtures:
            if fixture['fixture']['status']['short'] != 'FT':
                continue
                
            total_matches += 1
            
            # Calculate goals
            home_goals = fixture['score']['fulltime']['home']
            away_goals = fixture['score']['fulltime']['away']
            total_goals += home_goals + away_goals
            
            # Count result frequency
            result_key = f"{home_goals}-{away_goals}"
            results_count[result_key] = results_count.get(result_key, 0) + 1
            
            # Calculate cards
            if 'statistics' in fixture:
                for team_stats in fixture.get('statistics', []):
                    for stat in team_stats:
                        if stat['type'] == 'Yellow Cards':
                            total_yellows += int(stat['value'] or 0)
                        elif stat['type'] == 'Red Cards':
                            total_reds += int(stat['value'] or 0)
        
        # Calculate averages
        avg_goals = round(total_goals / total_matches, 2) if total_matches > 0 else 0
        avg_yellows = round(total_yellows / total_matches, 2) if total_matches > 0 else 0
        avg_reds = round(total_reds / total_matches, 2) if total_matches > 0 else 0
        
        # Get most common results
        sorted_results = sorted(results_count.items(), 
                              key=lambda x: (-x[1], x[0]))  # Sort by count desc, then result
        common_results = [
            {
                'result': result,
                'count': count,
                'percentage': round((count / total_matches) * 100, 1)
            }
            for result, count in sorted_results[:10]  # Top 10 most common results
        ]
        
        return {
            'avg_goals': avg_goals,
            'avg_yellows': avg_yellows,
            'avg_reds': avg_reds,
            'common_results': common_results
        }
