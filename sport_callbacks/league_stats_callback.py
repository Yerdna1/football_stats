from dash.dependencies import Input, Output, State
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from config import ALL_LEAGUES
from league_names import LEAGUE_NAMES
from sport_analyzers import LeagueAnalyzer
import dash
from dash import html, dcc
import logging

# Set up logging
logger = logging.getLogger(__name__)

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
        
     # Update layout to include category selector
    @app.callback(
        Output('league-goals-visualization-container', 'children'),
        [Input('league-category-selector', 'value')]
    )
    def update_visualization_container(selected_category):
        if selected_category == 'top':
            return dcc.Graph(id='top-leagues-chart')
        elif selected_category == 'middle':
            return dcc.Graph(id='middle-leagues-chart')
        elif selected_category == 'bottom':
            return dcc.Graph(id='bottom-leagues-chart')
        else:  # 'all'
            return html.Div([
                html.H3("Top Leagues by Average Goals", style={'textAlign': 'center', 'marginTop': '20px'}),
                dcc.Graph(id='top-leagues-chart'),
                html.H3("Mid-Tier Leagues by Average Goals", style={'textAlign': 'center', 'marginTop': '20px'}),
                dcc.Graph(id='middle-leagues-chart'),
                html.H3("Bottom Leagues by Average Goals", style={'textAlign': 'center', 'marginTop': '20px'}),
                dcc.Graph(id='bottom-leagues-chart')
            ])
        
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
                    print("DataFrame is empty! No league data collected.")
                    raise ValueError("No data available")
                else:
                    print(f"Successfully created DataFrame with {len(df)} leagues")
                
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
        
    # Separate callback for the new split charts
    @app.callback(
        [Output('top-leagues-chart', 'figure'),
         Output('middle-leagues-chart', 'figure'),
         Output('bottom-leagues-chart', 'figure')],
        Input('stats-league-dropdown', 'value')  # Used to trigger updates
    )
    def update_split_goals_comparison(_):
            try:
                # Get statistics for all leagues
                league_stats = []
                print("Starting to collect league statistics...")
                
                for league_id, league_info in LEAGUE_NAMES.items():
                    if isinstance(league_id, int):  # Skip ALL_LEAGUES entry
                        try:
                            print(f"Fetching fixtures for league ID {league_id} ({league_info.get('name', 'Unknown')})")
                            fixtures = api.fetch_fixtures(league_id)
                            
                            if fixtures:
                                print(f"Got {len(fixtures)} fixtures for league {league_id}")
                                total_goals = 0
                                total_matches = 0
                                
                                for fixture in fixtures:
                                    if fixture['fixture']['status']['short'] == 'FT':
                                        total_matches += 1
                                        home_goals = fixture['score']['fulltime']['home']
                                        away_goals = fixture['score']['fulltime']['away']
                                        total_goals += (home_goals + away_goals)
                                
                                if total_matches > 0:
                                    avg_goals = round(total_goals / total_matches, 2)
                                    print(f"League {league_info.get('name', 'Unknown')}: {total_goals} goals in {total_matches} matches, avg: {avg_goals}")
                                    
                                    # Get abbreviated country and league names
                                    country_name = league_info.get('country', '')
                                    league_name = league_info.get('name', '')
                                    
                                    # Store complete data
                                    league_stats.append({
                                        'league_name': league_name,
                                        'flag_url': league_info.get('flag', ''),
                                        'avg_goals': avg_goals,
                                        'total_goals': total_goals,
                                        'matches': total_matches,
                                        'country': country_name
                                    })
                            else:
                                print(f"No fixtures found for league {league_id}")
                        except Exception as e:
                            print(f"Error processing league {league_id}: {str(e)}")
                            continue
                
                # Debug check
                print(f"Collected stats for {len(league_stats)} leagues")
                if not league_stats:
                    print("WARNING: No league statistics were collected!")
                
                # Sort by average goals
                league_stats = sorted(league_stats, key=lambda x: x['avg_goals'], reverse=True)
                
                if not league_stats:
                    raise ValueError("No data available")
                
                # Split into three categories
                total_leagues = len(league_stats)
                print(f"Total leagues with data: {total_leagues}")
                
                top_count = min(15, total_leagues // 3 + (1 if total_leagues % 3 > 0 else 0))
                middle_count = min(15, total_leagues // 3 + (1 if total_leagues % 3 > 1 else 0))
                
                top_leagues = league_stats[:top_count]
                middle_leagues = league_stats[top_count:top_count+middle_count]
                bottom_leagues = league_stats[top_count+middle_count:]
                
                print(f"Split into: {len(top_leagues)} top leagues, {len(middle_leagues)} middle leagues, {len(bottom_leagues)} bottom leagues")
                
                # Create DataFrames for plotting
                top_df = pd.DataFrame(top_leagues)
                middle_df = pd.DataFrame(middle_leagues)
                bottom_df = pd.DataFrame(bottom_leagues)
                
                # Function to create a basic chart with color gradient 
                def create_chart_with_gradient(df, title, color_scale='Blues'):
                    if df.empty:
                        print(f"Empty DataFrame for {title} chart!")
                        # Return empty figure if no data
                        empty_fig = px.bar(title=f"{title} - No data available")
                        empty_fig.update_layout(height=400)
                        return empty_fig
                    
                    print(f"Creating {title} chart with {len(df)} leagues")
                    # Create bar chart
                    fig = px.bar(
                        df, 
                        x='league_name',
                        y='avg_goals',
                        title=title,
                        labels={'league_name': 'League', 'avg_goals': 'Average Goals per Match'},
                        text=df['avg_goals'].round(2),
                        color='avg_goals',
                        color_continuous_scale=color_scale,
                        height=500,
                        width=1000  # Fixed width for better fit
                    )
                    
                    # Customize layout
                    fig.update_traces(
                        texttemplate='%{text}',
                        textposition='outside',
                        marker_line_color='rgb(8,48,107)',
                        marker_line_width=1.5,
                        width=0.7  # Make bars narrower
                    )
                    
                    # Improve layout
                    fig.update_layout(
                        xaxis_tickangle=45,
                        margin=dict(t=60, l=50, r=50, b=150),
                        plot_bgcolor='rgba(248,249,250,0.5)',
                        paper_bgcolor='white',
                        font_family="Arial, sans-serif",
                        title_font=dict(size=18, color='rgb(8,48,107)'),
                        showlegend=False,
                        coloraxis_showscale=False
                    )
                    
                    # Add grid lines and improve axes
                    fig.update_xaxes(
                        showgrid=False,
                        showline=True,
                        linewidth=1,
                        linecolor='lightgrey',
                        title_font=dict(size=14)
                    )
                    
                    fig.update_yaxes(
                        gridcolor='lightgrey',
                        showline=True,
                        linewidth=1,
                        linecolor='lightgrey',
                        range=[0, max(df['avg_goals']) * 1.1],  # Add 10% padding to y-axis
                        title_font=dict(size=14)
                    )
                    
                    # Add hover data with more information
                    fig.update_traces(
                        hovertemplate='<b>%{x}</b><br>Country: %{customdata[2]}<br>Average Goals: %{y:.2f}<br>Total Goals: %{customdata[0]}<br>Matches: %{customdata[1]}',
                        customdata=df[['total_goals', 'matches', 'country']].values
                    )
                    
                    return fig
                
                # Create individual charts
                top_fig = create_chart_with_gradient(top_df, "Top Leagues by Average Goals", 'Blues')
                middle_fig = create_chart_with_gradient(middle_df, "Mid-Tier Leagues by Average Goals", 'Greens')
                bottom_fig = create_chart_with_gradient(bottom_df, "Bottom Leagues by Average Goals", 'Oranges')
                
                print("Successfully created all three charts")
                return top_fig, middle_fig, bottom_fig
                
            except Exception as e:
                print(f"Error creating goals comparison charts: {str(e)}")
                empty_fig = px.bar(title="No data available")
                empty_fig.update_layout(
                    xaxis_title="League",
                    yaxis_title="Average Goals per Match",
                    height=400
                )
                return empty_fig, empty_fig, empty_fig
