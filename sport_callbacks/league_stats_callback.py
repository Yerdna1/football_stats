from dash.dependencies import Input, Output
from datetime import datetime
import pandas as pd
import plotly.express as px
from config import ALL_LEAGUES, LEAGUE_NAMES
from sport_analyzers import LeagueAnalyzer

def setup_league_stats_callbacks(app, api):
    @app.callback(
        [Output('avg-goals-stat', 'children'),
        Output('avg-yellow-stat', 'children'),
        Output('avg-red-stat', 'children'),
        Output('common-results-table', 'data')],
        Input('stats-league-dropdown', 'value')
             )
    def update_league_stats(league_id):
            if not league_id:
                return "N/A", "N/A", "N/A", []
                
            try:
                # Handle ALL_LEAGUES case
                if league_id == ALL_LEAGUES:
                    fixtures = LeagueAnalyzer.get_all_leagues_fixtures(api)
                else:
                    fixtures = api.fetch_fixtures(league_id)

                if not fixtures:
                    return "N/A", "N/A", "N/A", []
                
                # Calculate statistics
                stats = LeagueAnalyzer.calculate_league_stats(fixtures)
                
                return (
                    f"{stats['avg_goals']:.2f}",
                    f"{stats['avg_yellows']:.2f}",
                    f"{stats['avg_reds']:.2f}",
                    stats['common_results']
                )
            except Exception as e:
                print(f"Error calculating league stats: {str(e)}")
                return "N/A", "N/A", "N/A", []   
        
         # League Goals Comparison Callback
    @app.callback(
            Output('league-goals-comparison', 'figure'),
            Input('stats-league-dropdown', 'value')  # We'll use this to trigger updates
        )
    def update_goals_comparison(_):
            try:
                # Get statistics for all leagues
                league_stats = []
                
                for league_id, league_info in LEAGUE_NAMES.items():
                    if isinstance(league_id, int):  # Skip ALL_LEAGUES entry
                        try:
                            fixtures = api.fetch_fixtures(league_id)
                            if fixtures:
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
                
                # Sort by average goals
                league_stats = sorted(league_stats, key=lambda x: x['avg_goals'], reverse=True)
                
                # Create DataFrame for plotting
                df = pd.DataFrame(league_stats)
                
                if df.empty:
                    raise ValueError("No data available")
                
                # Create bar chart
                fig = px.bar(df, 
                            x='league', 
                            y='avg_goals',
                            title='Average Goals per Match by League',
                            labels={'league': 'League', 
                                   'avg_goals': 'Average Goals per Match'},
                            text=df['avg_goals'].round(2))  # Show values on bars
                
                # Customize layout
                fig.update_traces(
                    texttemplate='%{text}',
                    textposition='outside',
                    marker_color='rgb(55, 83, 109)'
                )
                
                fig.update_layout(
                    xaxis_tickangle=45,
                    margin=dict(t=50, l=50, r=50, b=120),  # Increased bottom margin
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    font_family="Arial, sans-serif",
                    showlegend=False,
                    height=600,  # Make chart taller to accommodate all leagues
                    yaxis_title="Average Goals per Match",
                    xaxis_title="League"
                )
                
                fig.update_xaxes(
                    gridcolor='lightgrey',
                    showline=True,
                    linewidth=1,
                    linecolor='lightgrey'
                )
                
                fig.update_yaxes(
                    gridcolor='lightgrey',
                    showline=True,
                    linewidth=1,
                    linecolor='lightgrey',
                    range=[0, max(df['avg_goals']) * 1.1]  # Add 10% padding to y-axis
                )
                
                return fig
                
            except Exception as e:
                print(f"Error creating goals comparison chart: {str(e)}")
                empty_fig = px.bar(title="No data available")
                empty_fig.update_layout(
                    xaxis_title="League",
                    yaxis_title="Average Goals per Match",
                    height=400
                )
                return empty_fig 
        