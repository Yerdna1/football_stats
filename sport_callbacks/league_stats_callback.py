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
    
    # League Goals Comparison Callback - Improved with split charts
    @app.callback(
        [Output('top-leagues-chart', 'figure'),
         Output('middle-leagues-chart', 'figure'),
         Output('bottom-leagues-chart', 'figure')],
        Input('stats-league-dropdown', 'value')  # Used to trigger updates
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
                                # Store flag_url separately
                                league_stats.append({
                                    'league_name': league_info['name'],
                                    'flag_url': league_info['flag'],
                                    'avg_goals': avg_goals,
                                    'total_goals': total_goals,
                                    'matches': total_matches,
                                    'country': league_info['country']
                                })
                    except Exception as e:
                        print(f"Error processing league {league_id}: {str(e)}")
                        continue
            
            # Sort by average goals
            league_stats = sorted(league_stats, key=lambda x: x['avg_goals'], reverse=True)
            
            if not league_stats:
                raise ValueError("No data available")
            
            # Split into three categories
            total_leagues = len(league_stats)
            top_count = min(15, total_leagues // 3 + (1 if total_leagues % 3 > 0 else 0))
            middle_count = min(15, total_leagues // 3 + (1 if total_leagues % 3 > 1 else 0))
            
            top_leagues = league_stats[:top_count]
            middle_leagues = league_stats[top_count:top_count+middle_count]
            bottom_leagues = league_stats[top_count+middle_count:]
            
            # Create DataFrames for plotting
            top_df = pd.DataFrame(top_leagues)
            middle_df = pd.DataFrame(middle_leagues)
            bottom_df = pd.DataFrame(bottom_leagues)
            
            # Function to create a chart with flag images
            def create_chart_with_flags(df, title, color_start=0.3, color_end=1.0):
                if df.empty:
                    # Return empty figure if no data
                    return px.bar(title="No data available")
                
                # Create bar chart with more visual appeal
                fig = px.bar(
                    df, 
                    x='league_name',
                    y='avg_goals',
                    title=title,
                    labels={'league_name': 'League', 'avg_goals': 'Average Goals per Match'},
                    text=df['avg_goals'].round(2),
                    color='avg_goals',
                    color_continuous_scale=[(0, f'rgba(8, 81, 156, {color_start})'), (1, f'rgba(8, 81, 156, {color_end})')],
                    height=500
                )
                
                # Customize layout
                fig.update_traces(
                    texttemplate='%{text}',
                    textposition='outside',
                    marker_line_color='rgb(8,48,107)',
                    marker_line_width=1.5,
                    opacity=0.85
                )
                
                # Improve layout
                fig.update_layout(
                    xaxis_tickangle=45,
                    margin=dict(t=80, l=50, r=50, b=150),  # Increased bottom margin for flags
                    plot_bgcolor='rgba(240,240,240,0.2)',
                    paper_bgcolor='white',
                    font_family="Arial, sans-serif",
                    font=dict(size=12),
                    title_font=dict(size=18, color='rgb(8,48,107)'),
                    showlegend=False,
                    coloraxis_showscale=False,
                    xaxis=dict(
                        tickmode='array',
                        tickvals=list(range(len(df))),
                        ticktext=['' for _ in range(len(df))]
                    )
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
                
                # Add flag images below the bars using annotations
                for i, row in enumerate(df.to_dict('records')):
                    # Add flag images
                    fig.add_layout_image(
                        dict(
                            source=row['flag_url'],
                            xref="x",
                            yref="paper",
                            x=i,
                            y=-0.15,
                            sizex=0.7,  # Slightly smaller
                            sizey=0.1,
                            xanchor="center",
                            yanchor="middle"
                        )
                    )
                    
                    # Add league name below flag
                    fig.add_annotation(
                        x=i,
                        y=-0.25,
                        text=row['league_name'],
                        showarrow=False,
                        xref="x",
                        yref="paper",
                        font=dict(
                            family="Arial, sans-serif",
                            size=10,
                            color="black"
                        ),
                        align="center"
                    )
                    
                    # Add country name for clarity
                    fig.add_annotation(
                        x=i,
                        y=-0.32,
                        text=row['country'],
                        showarrow=False,
                        xref="x",
                        yref="paper",
                        font=dict(
                            family="Arial, sans-serif",
                            size=8,
                            color="gray"
                        ),
                        align="center"
                    )
                
                # Add hover data with more information
                fig.update_traces(
                    hovertemplate='<b>%{x}</b><br>Average Goals: %{y:.2f}<br>Total Goals: %{customdata[0]}<br>Matches: %{customdata[1]}<br>Country: %{customdata[2]}',
                    customdata=df[['total_goals', 'matches', 'country']].values
                )
                
                return fig
            
            # Create individual charts
            top_fig = create_chart_with_flags(top_df, "Top Leagues by Average Goals", 0.7, 1.0)
            middle_fig = create_chart_with_flags(middle_df, "Mid-Tier Leagues by Average Goals", 0.5, 0.8)
            bottom_fig = create_chart_with_flags(bottom_df, "Bottom Leagues by Average Goals", 0.3, 0.6)
            
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
