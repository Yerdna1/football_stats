from collections import defaultdict
import pandas as pd
import plotly.express as px
from dash import html, dash_table, dcc

def update_detailed_stats(team_stats, statistics):
    """Update detailed team statistics"""
    for stat in statistics:
        type_name = stat.get('type', '')
        value = stat.get('value')
        
        if value is None:
            continue
        
        # Convert percentage strings
        if isinstance(value, str):
            if '%' in value:
                try:
                    value = float(value.strip('%'))
                except (ValueError, TypeError):
                    continue
            else:
                try:
                    value = float(value) if '.' in value else int(value)
                except (ValueError, TypeError):
                    continue
        
        # Update specific statistics
        if type_name == 'Shots on Goal':
            team_stats['shots_on_target'] += value
        elif type_name == 'Shots off Goal':
            team_stats['shots_off_target'] += value
        elif type_name == 'Total Shots':
            team_stats['shots_total'] += value
        elif type_name == 'Blocked Shots':
            team_stats['blocked_shots'] += value
        elif type_name == 'Shots insidebox':
            team_stats['shots_inside_box'] += value
        elif type_name == 'Shots outsidebox':
            team_stats['shots_outside_box'] += value
        elif type_name == 'Fouls':
            team_stats['fouls'] += value
        elif type_name == 'Corner Kicks':
            team_stats['corners'] += value
        elif type_name == 'Offsides':
            team_stats['offsides'] += value
        elif type_name == 'Ball Possession':
            team_stats['possession'].append(value)
        elif type_name == 'Yellow Cards':
            team_stats['yellow_cards'] += value
        elif type_name == 'Red Cards' and value is not None:
            team_stats['red_cards'] += value
        elif type_name == 'Goalkeeper Saves':
            team_stats['goalkeeper_saves'] += value
        elif type_name == 'Total passes':
            team_stats['total_passes'] += value
        elif type_name == 'Passes accurate':
            team_stats['passes_accurate'] += value
        elif type_name == 'Passes %':
            team_stats['pass_accuracy'].append(value)
        elif type_name == 'expected_goals':
            team_stats['expected_goals'] += value
        elif type_name == 'goals_prevented' and value is not None:
            team_stats['goals_prevented'] += value

def calculate_derived_stats(team_stats):
    """Calculate derived statistics"""
    for stats in team_stats.values():
        matches = stats['total_matches']
        if matches > 0:
            stats['points'] = (stats['wins'] * 3) + stats['draws']
            stats['ppg'] = stats['points'] / matches
            stats['goals_per_game'] = stats['goals_scored'] / matches
            stats['conceded_per_game'] = stats['goals_conceded'] / matches
            stats['avg_possession'] = sum(stats['possession']) / len(stats['possession']) if stats['possession'] else 0
            stats['avg_pass_accuracy'] = sum(stats['pass_accuracy']) / len(stats['pass_accuracy']) if stats['pass_accuracy'] else 0

def check_fixture_completeness(fixture):
    """Check if fixture has all required data"""
    required_fields = ['events', 'lineups', 'statistics', 'players']
    return all(fixture.get(field) for field in required_fields)

def analyze_data_quality(fixtures_data):
    """Analyze fixtures data quality"""
    try:
        quality_stats = {
            'total_fixtures': len(fixtures_data),
            'leagues': defaultdict(lambda: {
                'fixtures_count': 0,
                'seasons': set(),  # Using set for unique seasons
                'teams': set(),    # Using set for unique teams
                'players': set(),  # Using set for unique players
                'complete_data': 0,
                'missing_data': 0,
                'name': ''  # Initialize name
            })
        }
        
        # Analyze each fixture
        for fixture in fixtures_data:
            try:
                # Safely get league data with fallbacks
                league_data = fixture.get('league', {})
                league_id = str(league_data.get('id', ''))  # Convert to string
                league_name = league_data.get('name', 'Unknown')
                season = str(league_data.get('season', ''))  # Convert to string
                
                # Skip if no league ID
                if not league_id:
                    continue
                
                # Update league stats
                quality_stats['leagues'][league_id]['fixtures_count'] += 1
                quality_stats['leagues'][league_id]['name'] = league_name
                if season:
                    quality_stats['leagues'][league_id]['seasons'].add(season)
                
                # Safely get team data
                teams_data = fixture.get('teams', {})
                home_team = teams_data.get('home', {}).get('id')
                away_team = teams_data.get('away', {}).get('id')
                
                if home_team:
                    quality_stats['leagues'][league_id]['teams'].add(str(home_team))
                if away_team:
                    quality_stats['leagues'][league_id]['teams'].add(str(away_team))
                
                # Check data completeness
                is_complete = check_fixture_completeness(fixture)
                if is_complete:
                    quality_stats['leagues'][league_id]['complete_data'] += 1
                else:
                    quality_stats['leagues'][league_id]['missing_data'] += 1
                
                # Process players safely
                players_data = fixture.get('players', [])
                for team_data in players_data:
                    for player in team_data.get('players', []):
                        player_id = str(player.get('player', {}).get('id', ''))
                        if player_id:
                            quality_stats['leagues'][league_id]['players'].add(player_id)
            
            except Exception as e:
                print(f"Error processing fixture: {e}")
                continue
        
        # Convert sets to lengths for the final output
        for league_id in quality_stats['leagues']:
            quality_stats['leagues'][league_id]['seasons'] = len(quality_stats['leagues'][league_id]['seasons'])
            quality_stats['leagues'][league_id]['teams'] = len(quality_stats['leagues'][league_id]['teams'])
            quality_stats['leagues'][league_id]['players'] = len(quality_stats['leagues'][league_id]['players'])
        
        return quality_stats
        
    except Exception as e:
        print(f"Error in analyze_data_quality: {e}")
        return None

def create_data_quality_report(stats):
    """Create data quality report"""
    if not stats:
        return html.Div("No data available")
    
    try:
        league_rows = []
        for league_id, league_data in stats['leagues'].items():
            fixtures_count = league_data['fixtures_count']
            if fixtures_count > 0:
                quality_percentage = (league_data['complete_data'] / fixtures_count * 100) if fixtures_count > 0 else 0
                
                league_rows.append({
                    'League': str(league_data['name']),
                    'Total Fixtures': int(fixtures_count),
                    'Seasons': int(league_data['seasons']),
                    'Teams': int(league_data['teams']),
                    'Players': int(league_data['players']),
                    'Complete Data': int(league_data['complete_data']),
                    'Missing Data': int(league_data['missing_data']),
                    'Data Quality %': f"{quality_percentage:.1f}%"
                })
        
        return html.Div([
            html.Div([
                html.H3("Data Quality Overview", className='text-xl font-bold mb-4'),
                html.P(f"Total Fixtures in Database: {stats['total_fixtures']}", className='mb-2'),
                html.P(f"Total Leagues: {len(stats['leagues'])}", className='mb-4'),
            ]),
            
            html.Div([
                html.H3("League-wise Data Quality", className='text-xl font-bold mb-4'),
                dash_table.DataTable(
                    data=league_rows,
                    columns=[{'name': col, 'id': col} for col in league_rows[0].keys()],
                    style_table={'overflowX': 'auto'},
                    style_cell={'textAlign': 'left', 'padding': '10px'},
                    style_header={
                        'backgroundColor': 'rgb(230, 230, 230)',
                        'fontWeight': 'bold'
                    },
                    sort_action='native',
                    filter_action='native'
                ) if league_rows else html.Div("No league data available")
            ], className='mb-8')
        ])
    except Exception as e:
        print(f"Error creating data quality report: {e}")
        return html.Div(f"Error creating report: {str(e)}")
def create_team_analysis_report(team_stats, quality_metrics):
    """Create team analysis report"""
    try:
        # Create table rows with all statistics
        rows = []
        for team_id, stats in team_stats.items():
            if stats['total_matches'] > 0:
                rows.append({
                    'Team': str(stats['name']),
                    'Total Matches': int(stats['total_matches']),
                    'Home/Away': f"{stats['home_matches']}/{stats['away_matches']}",
                    'W/D/L': f"{stats['wins']}/{stats['draws']}/{stats['losses']}",
                    'Points': stats['points'],
                    'PPG': f"{stats.get('ppg', 0):.2f}",
                    'Goals F/A': f"{stats['goals_scored']}/{stats['goals_conceded']}",
                    'Goals pg': f"{stats.get('goals_per_game', 0):.2f}",
                    'Home Goals': stats['home_goals'],
                    'Away Goals': stats['away_goals'],
                    'Clean Sheets': stats['clean_sheets'],
                    'Failed to Score': stats['failed_to_score'],
                    'Shots Total': stats['shots_total'],
                    'On Target': stats['shots_on_target'],
                    'Inside Box': stats['shots_inside_box'],
                    'Outside Box': stats['shots_outside_box'],
                    'Blocked': stats['blocked_shots'],
                    'Corners': stats['corners'],
                    'Fouls': stats['fouls'],
                    'Offsides': stats['offsides'],
                    'Cards (Y/R)': f"{stats['yellow_cards']}/{stats['red_cards']}",
                    'Passes': stats['total_passes'],
                    'Accurate Passes': stats['passes_accurate'],
                    'Pass Acc.%': f"{stats.get('avg_pass_accuracy', 0):.1f}%",
                    'Possession%': f"{stats.get('avg_possession', 0):.1f}%",
                    'xG': f"{stats['expected_goals']:.2f}",
                    'Goals Prevented': f"{stats['goals_prevented']:.2f}" if stats['goals_prevented'] else "0"
                })
        
        if not rows:
            return html.Div("No team statistics available")
        
        return html.Div([
            # Data Quality Overview
            html.Div([
                html.H3("Data Quality Overview", className='text-xl font-bold mb-4'),
                html.P(f"Total Fixtures: {quality_metrics['total_fixtures']}", className='mb-2'),
                html.P(f"Complete Data: {quality_metrics['complete_data']}", className='mb-2'),
                html.P(f"Missing Data: {quality_metrics['missing_data']}", className='mb-2'),
                html.P(f"Data Quality: {(quality_metrics['complete_data'] / quality_metrics['total_fixtures'] * 100):.1f}%", className='mb-4')
            ], className='mb-8'),
            
            # Team Statistics Table
            html.Div([
                html.H3("Team Performance Analysis", className='text-xl font-bold mb-4'),
                dash_table.DataTable(
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
            ], className='mb-8'),
            
            # Visualizations
            html.Div([
                html.H3("Team Performance Visualizations", className='text-xl font-bold mb-4'),
                html.Div([
                    create_team_goals_visualization(team_stats),
                    create_team_stats_visualization(team_stats)
                ], className='grid grid-cols-1 md:grid-cols-2 gap-4')
            ])
        ])
    except Exception as e:
        print(f"Error creating team analysis report: {e}")
        return html.Div(f"Error creating team report: {str(e)}")

def create_team_goals_visualization(team_stats):
    """Create team goals visualization"""
    try:
        data = []
        for team_id, stats in team_stats.items():
            if stats['total_matches'] > 0:
                data.append({
                    'Team': stats['name'],
                    'Goals pg': stats.get('goals_per_game', 0),
                    'Conceded pg': stats.get('conceded_per_game', 0),
                    'xG pg': stats['expected_goals'] / stats['total_matches'],
                    'Home Goals pg': stats['home_goals'] / stats['home_matches'] if stats['home_matches'] > 0 else 0,
                    'Away Goals pg': stats['away_goals'] / stats['away_matches'] if stats['away_matches'] > 0 else 0
                })
        
        fig = px.bar(
            data,
            x='Team',
            y=['Goals pg', 'Conceded pg', 'xG pg', 'Home Goals pg', 'Away Goals pg'],
            title='Goals Analysis per Game',
            barmode='group',
            height=400
        )
        
        fig.update_layout(
            xaxis_tickangle=-45,
            legend_title='Metrics',
            margin=dict(t=50, b=100)
        )
        
        return dcc.Graph(figure=fig)
        
    except Exception as e:
        print(f"Error creating goals visualization: {e}")
        return html.Div(f"Error creating visualization: {str(e)}")

def create_team_stats_visualization(team_stats):
    """Create additional team statistics visualization"""
    try:
        data = []
        for team_id, stats in team_stats.items():
            if stats['total_matches'] > 0:
                data.append({
                    'Team': stats['name'],
                    'Shot Accuracy %': (stats['shots_on_target'] / stats['shots_total'] * 100) if stats['shots_total'] > 0 else 0,
                    'Pass Accuracy %': stats.get('avg_pass_accuracy', 0),
                    'Possession %': stats.get('avg_possession', 0),
                    'Inside Box %': (stats['shots_inside_box'] / stats['shots_total'] * 100) if stats['shots_total'] > 0 else 0
                })
        
        fig = px.line(
            data,
            x='Team',
            y=['Shot Accuracy %', 'Pass Accuracy %', 'Possession %', 'Inside Box %'],
            title='Team Performance Metrics',
            height=400
        )
        
        fig.update_layout(
            xaxis_tickangle=-45,
            legend_title='Metrics',
            margin=dict(t=50, b=100)
        )
        
        return dcc.Graph(figure=fig)
        
    except Exception as e:
        print(f"Error creating stats visualization: {e}")
        return html.Div(f"Error creating visualization: {str(e)}")

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
                    try:
                        player = player_data.get('player', {})
                        stats = player_data.get('statistics', [{}])[0]
                        player_id = str(player.get('id', ''))
                        
                        if not player_id:
                            continue
                        
                        # Basic info
                        player_stats[player_id]['name'] = player.get('name', '')
                        player_stats[player_id]['team'] = team_data.get('team', {}).get('name', '')
                        
                        # Game stats
                        games = stats.get('games', {})
                        if games.get('minutes'):
                            player_stats[player_id]['appearances'] += 1
                            player_stats[player_id]['minutes'] += int(games.get('minutes', 0))
                        
                        if games.get('rating'):
                            try:
                                rating = float(games['rating'])
                                player_stats[player_id]['rating'].append(rating)
                            except (ValueError, TypeError):
                                pass
                        
                        # Goals and assists
                        goals_data = stats.get('goals', {})
                        player_stats[player_id]['goals'] += int(goals_data.get('total', 0) or 0)
                        player_stats[player_id]['assists'] += int(goals_data.get('assists', 0) or 0)
                        
                        # Cards
                        cards_data = stats.get('cards', {})
                        player_stats[player_id]['yellow_cards'] += int(cards_data.get('yellow', 0) or 0)
                        player_stats[player_id]['red_cards'] += int(cards_data.get('red', 0) or 0)
                        
                        # Shots
                        shots_data = stats.get('shots', {})
                        player_stats[player_id]['shots_total'] += int(shots_data.get('total', 0) or 0)
                        player_stats[player_id]['shots_on'] += int(shots_data.get('on', 0) or 0)
                        
                        # Passes
                        passes_data = stats.get('passes', {})
                        player_stats[player_id]['passes_total'] += int(passes_data.get('total', 0) or 0)
                        if passes_data.get('accuracy'):
                            try:
                                accuracy = float(passes_data['accuracy'])
                                player_stats[player_id]['passes_accuracy'].append(accuracy)
                            except (ValueError, TypeError):
                                pass
                        
                        # Tackles and interceptions
                        tackles_data = stats.get('tackles', {})
                        player_stats[player_id]['tackles'] += int(tackles_data.get('total', 0) or 0)
                        player_stats[player_id]['interceptions'] += int(tackles_data.get('interceptions', 0) or 0)
                        
                        # Duels
                        duels_data = stats.get('duels', {})
                        player_stats[player_id]['duels_total'] += int(duels_data.get('total', 0) or 0)
                        player_stats[player_id]['duels_won'] += int(duels_data.get('won', 0) or 0)
                    
                    except Exception as e:
                        print(f"Error processing player data: {e}")
                        continue
        
        except Exception as e:
            print(f"Error processing fixture players: {e}")
            continue
    
    return player_stats

def create_player_statistics_table(player_stats):
    """Create a Pandas DataFrame with player statistics."""
    rows = []
    for player_id, stats in player_stats.items():
        if stats['appearances'] > 0:  # Only show players who played
            avg_rating = sum(stats['rating']) / len(stats['rating']) if stats['rating'] else 0
            pass_accuracy = sum(stats['passes_accuracy']) / len(stats['passes_accuracy']) if stats['passes_accuracy'] else 0

            rows.append({
                'Name': stats['name'],
                'Team': stats['team'],
                'Apps': stats['appearances'],
                'Minutes': stats['minutes'],
                'Goals': stats['goals'],
                'Assists': stats['assists'],
                'Rating': avg_rating,  # Store as numeric for sorting/calculations
                'Yellow Cards': stats['yellow_cards'],
                'Red Cards': stats['red_cards'],
                'Shots': stats['shots_total'],
                'Shots on Target': stats['shots_on'],
                'Passes': stats['passes_total'],
                'Pass Accuracy': pass_accuracy, # Store as numeric for sorting/calculations
                'Tackles': stats['tackles'],
                'Interceptions': stats['interceptions'],
                'Duels Won': (stats['duels_won'] / stats['duels_total'] * 100) if stats['duels_total'] > 0 else 0 # Store as numeric
            })

    df = pd.DataFrame(rows)

    # Format columns for display *after* DataFrame creation
    df['Rating'] = df['Rating'].apply(lambda x: f"{x:.2f}")
    df['Pass Accuracy'] = df['Pass Accuracy'].apply(lambda x: f"{x:.1f}%")
    df['Duels Won'] = df['Duels Won'].apply(lambda x: f"{x:.1f}%")

    return df # Return the Pandas DataFrame