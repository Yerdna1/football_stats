from collections import defaultdict
import pandas as pd
import plotly.express as px
from dash import html, dash_table, dcc

def analyze_data_quality(db):
    """Analyze fixtures data quality from Firebase"""
    try:
        fixtures = db.collection('fixtures').stream()
        fixtures_data = [fixture.to_dict() for fixture in fixtures]
        
        print(f"Total fixtures loaded: {len(fixtures_data)}")  # Debug print
        
        # Basic Counts
        stats = {
            'total_fixtures': len(fixtures_data),
            'leagues': defaultdict(lambda: {
                'fixtures_count': 0,
                'seasons': set(),
                'teams': set(),
                'players': set(),
                'complete_data': 0,
                'missing_data': 0
            })
        }
        
        # Analyze each fixture
        for fixture in fixtures_data:
            try:
                league_id = fixture['league']['id']
                league_name = fixture['league']['name']
                season = fixture['league']['season']
                
                print(f"Processing fixture for league: {league_name}, season: {season}")  # Debug print
                
                # Update league stats
                stats['leagues'][league_id]['fixtures_count'] += 1
                stats['leagues'][league_id]['seasons'].add(season)
                stats['leagues'][league_id]['name'] = league_name
                
                # Check teams
                home_team = fixture['teams']['home']['id']
                away_team = fixture['teams']['away']['id']
                stats['leagues'][league_id]['teams'].add(home_team)
                stats['leagues'][league_id]['teams'].add(away_team)
                
                # Check data completeness
                if check_fixture_completeness(fixture):
                    stats['leagues'][league_id]['complete_data'] += 1
                else:
                    stats['leagues'][league_id]['missing_data'] += 1
                
                # Collect players
                if 'players' in fixture:
                    for team_data in fixture['players']:
                        for player in team_data['players']:
                            stats['leagues'][league_id]['players'].add(player['player']['id'])
            
            except Exception as e:
                print(f"Error processing fixture: {e}")
                continue
        
        return stats
    
    except Exception as e:
        print(f"Error analyzing data: {e}")
        return None

def check_fixture_completeness(fixture):
    required_fields = [
        ('events', []),
        ('lineups', []),
        ('statistics', []),
        ('players', [])
    ]
    
    for field, default in required_fields:
        if field not in fixture or fixture[field] == default:
            print(f"Missing or empty field: {field}")
            return False
    return True

def create_data_quality_report(stats):
    """Create a report of data quality"""
    if not stats:
        return html.Div("No data available")
    
    league_rows = []
    for league_id, league_data in stats['leagues'].items():
        fixtures_count = league_data['fixtures_count']
        if fixtures_count > 0:  # Avoid division by zero
            league_rows.append({
                'League': league_data['name'],
                'Total Fixtures': fixtures_count,
                'Seasons': len(league_data['seasons']),
                'Teams': len(league_data['teams']),
                'Players': len(league_data['players']),
                'Complete Data': league_data['complete_data'],
                'Missing Data': league_data['missing_data'],
                'Data Quality %': f"{(league_data['complete_data'] / fixtures_count * 100):.1f}%"
            })
    
    return html.Div([
        # Overall Summary
        html.Div([
            html.H3("Data Quality Overview", className='text-xl font-bold mb-4'),
            html.P(f"Total Fixtures in Database: {stats['total_fixtures']}", className='mb-2'),
            html.P(f"Total Leagues: {len(stats['leagues'])}", className='mb-4'),
        ]),
        
        # League-wise Summary
        html.Div([
            html.H3("League-wise Data Quality", className='text-xl font-bold mb-4'),
            dash_table.DataTable(
                data=league_rows,
                columns=[{'name': col, 'id': col} for col in [
                    'League', 'Total Fixtures', 'Seasons', 'Teams', 
                    'Players', 'Complete Data', 'Missing Data', 'Data Quality %'
                ]],
                style_table={'overflowX': 'auto'},
                style_cell={'textAlign': 'left', 'padding': '10px'},
                style_header={
                    'backgroundColor': 'rgb(230, 230, 230)',
                    'fontWeight': 'bold'
                },
                sort_action='native'
            )
        ], className='mb-8'),
    ])

def create_player_statistics(fixtures_data):
    """Analyze player statistics from fixtures"""
    player_stats = defaultdict(lambda: {
        'name': '',
        'team': '',
        'appearances': 0,
        'minutes': 0,
        'goals': 0,
        'assists': 0,
        'yellow_cards': 0,
        'red_cards': 0,
        'rating': [],
        'shots_total': 0,
        'shots_on': 0,
        'passes_total': 0,
        'passes_accuracy': [],
        'tackles': 0,
        'interceptions': 0,
        'duels_total': 0,
        'duels_won': 0
    })
    
    for fixture in fixtures_data:
        try:
            for team_data in fixture.get('players', []):
                for player_data in team_data.get('players', []):
                    player = player_data['player']
                    stats = player_data['statistics'][0]
                    player_id = str(player['id'])
                    
                    # Basic info
                    player_stats[player_id]['name'] = player['name']
                    player_stats[player_id]['team'] = team_data['team']['name']
                    
                    # Game stats
                    if stats['games']['minutes']:
                        player_stats[player_id]['appearances'] += 1
                        player_stats[player_id]['minutes'] += stats['games']['minutes']
                    
                    if stats['games'].get('rating'):
                        player_stats[player_id]['rating'].append(float(stats['games']['rating']))
                    
                    # Goals and assists
                    if stats.get('goals'):
                        player_stats[player_id]['goals'] += stats['goals'].get('total', 0) or 0
                        player_stats[player_id]['assists'] += stats['goals'].get('assists', 0) or 0
                    
                    # Cards
                    if stats.get('cards'):
                        player_stats[player_id]['yellow_cards'] += stats['cards'].get('yellow', 0) or 0
                        player_stats[player_id]['red_cards'] += stats['cards'].get('red', 0) or 0
                    
                    # Shots
                    if stats.get('shots'):
                        player_stats[player_id]['shots_total'] += stats['shots'].get('total', 0) or 0
                        player_stats[player_id]['shots_on'] += stats['shots'].get('on', 0) or 0
                    
                    # Passes
                    if stats.get('passes'):
                        player_stats[player_id]['passes_total'] += stats['passes'].get('total', 0) or 0
                        if stats['passes'].get('accuracy'):
                            player_stats[player_id]['passes_accuracy'].append(float(stats['passes']['accuracy']))
                    
                    # Tackles and interceptions
                    if stats.get('tackles'):
                        player_stats[player_id]['tackles'] += stats['tackles'].get('total', 0) or 0
                        player_stats[player_id]['interceptions'] += stats['tackles'].get('interceptions', 0) or 0
                    
                    # Duels
                    if stats.get('duels'):
                        player_stats[player_id]['duels_total'] += stats['duels'].get('total', 0) or 0
                        player_stats[player_id]['duels_won'] += stats['duels'].get('won', 0) or 0
        
        except Exception as e:
            print(f"Error processing player statistics: {e}")
            continue
    
    return player_stats

def create_player_statistics_table(player_stats):
    """Create a table with player statistics"""
    rows = []
    for player_id, stats in player_stats.items():
        if stats['appearances'] > 0:  # Only show players who played
            avg_rating = sum(stats['rating'])/len(stats['rating']) if stats['rating'] else 0
            pass_accuracy = sum(stats['passes_accuracy'])/len(stats['passes_accuracy']) if stats['passes_accuracy'] else 0
            
            rows.append({
                'Name': stats['name'],
                'Team': stats['team'],
                'Apps': stats['appearances'],
                'Minutes': stats['minutes'],
                'Goals': stats['goals'],
                'Assists': stats['assists'],
                'Rating': f"{avg_rating:.2f}",
                'Yellow Cards': stats['yellow_cards'],
                'Red Cards': stats['red_cards'],
                'Shots': stats['shots_total'],
                'Shots on Target': stats['shots_on'],
                'Passes': stats['passes_total'],
                'Pass Accuracy': f"{pass_accuracy:.1f}%",
                'Tackles': stats['tackles'],
                'Interceptions': stats['interceptions'],
                'Duels Won': f"{(stats['duels_won']/stats['duels_total']*100):.1f}%" if stats['duels_total'] > 0 else "0%"
            })
    
    return dash_table.DataTable(
        data=rows,
        columns=[{'name': col, 'id': col} for col in rows[0].keys()],
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'left', 'padding': '10px'},
        style_header={
            'backgroundColor': 'rgb(230, 230, 230)',
            'fontWeight': 'bold'
        },
        sort_action='native',
        filter_action='native',
        page_size=20
    )