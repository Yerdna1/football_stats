from venv import logger
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
from sport_analyzers import WinlessStreakAnalyzer
from config import LEAGUE_NAMES 
 # Callback to update the winless streaks chart and data table
def setup_winless_streaks_callbacks(app, api):
    @app.callback(
            [Output('winless-streaks-chart', 'figure'),
             Output('last-matches-table', 'data')],
            [Input('winless-league-dropdown', 'value'),  # Changed from 'league-dropdown'
             Input('current-streak-filter', 'value')]
        )
    def update_winless_data(league_id, current_streak_filter):
            try:
                
                fixtures = api.fetch_fixtures(league_id)  # This will handle ALL_LEAGUES internally

                
               
                if not fixtures:
                    return px.bar(title="No data available"), []
                
                show_current_only = 'current' in current_streak_filter
                streaks = WinlessStreakAnalyzer.calculate_streaks(
                    fixtures, current_only=show_current_only)
                
                df = pd.DataFrame(list(streaks.items()), columns=['Team', 'Winless Streak'])
                df = df.sort_values('Winless Streak', ascending=False)
                
                # Create bar chart
                top_10_df = df.head(10)
                fig = px.bar(top_10_df, 
                             x='Team', 
                             y='Winless Streak',
                            title=f'Top Winless Streaks in {LEAGUE_NAMES.get(league_id, {}).get("name", "Selected League")}')

                
                fig.update_layout(
                    xaxis_tickangle=45,
                    margin=dict(t=50, l=50, r=50, b=100),
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    font_family="Arial, sans-serif",
                    showlegend=False
                )
                
                fig.update_traces(
                    marker_color='rgb(55, 83, 109)',
                    hovertemplate='Team: %{x}<br>Winless Streak: %{y}<extra></extra>'
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
                    linecolor='lightgrey'
                )
                
                # Create table data
                table_data = []
                for _, row in df.head(5).iterrows():
                    team = row['Team']
                    last_match = WinlessStreakAnalyzer.get_last_match(fixtures, team)
                    if last_match:
                        table_data.append({
                            'team': team,
                            'streak': int(row['Winless Streak']),
                            'result': last_match['result'],
                            'score': last_match['score'],
                            'date': last_match['date']
                        })
                
                return fig, table_data
                
            except Exception as e:
                logger.error(f"Error updating data: {str(e)}")
                return px.bar(title="Error loading data"), []