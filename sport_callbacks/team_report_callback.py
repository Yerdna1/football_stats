from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

@app.callback(
    [Output('team-statistics-table', 'columns'),
     Output('team-statistics-table', 'data'),
     Output('team-quality-report-table', 'columns'),
     Output('team-quality-report-table', 'data'),
     Output('team-report-table', 'columns'),
     Output('team-report-table', 'data')],
    [Input('analyze-data-button', 'n_clicks')],
    [State('firebase-analysis-tab', 'value')]
)
def update_team_tables(n_clicks, selected_tab):
    if n_clicks is None or selected_tab != 'firebase-analysis-tab':
        raise PreventUpdate  # Do nothing if the button hasn't been clicked or the tab isn't selected
    
    # Fetch fixtures data (replace this with your actual data fetching logic)
    fixtures_data = fetch_fixtures_with_retry(db)
    
    # Generate team statistics
    team_stats = create_team_statistics(fixtures_data)
    
    # Generate team quality report
    team_quality = analyze_team_data_quality(fixtures_data)
    
    # Generate team report
    team_report, _ = create_team_report(team_stats, team_quality)
    
    # Prepare columns and data for the tables
    team_stats_columns = [{'name': col, 'id': col} for col in [
        'Team', 'League', 'Matches Played', 'Wins', 'Draws', 'Losses', 
        'Goals Scored', 'Goals Conceded', 'Clean Sheets', 'Failed to Score', 
        'Yellow Cards', 'Red Cards', 'Avg Possession', 'Avg Shots', 
        'Avg Passes', 'Avg Tackles', 'Avg Interceptions'
    ]]
    team_stats_data = [
        {
            'Team': stats['name'],
            'League': stats['league'],
            'Matches Played': stats['matches_played'],
            'Wins': stats['wins'],
            'Draws': stats['draws'],
            'Losses': stats['losses'],
            'Goals Scored': stats['goals_scored'],
            'Goals Conceded': stats['goals_conceded'],
            'Clean Sheets': stats['clean_sheets'],
            'Failed to Score': stats['failed_to_score'],
            'Yellow Cards': stats['yellow_cards'],
            'Red Cards': stats['red_cards'],
            'Avg Possession': f"{sum(stats['avg_possession']) / len(stats['avg_possession']):.1f}%" if stats['avg_possession'] else "0%",
            'Avg Shots': f"{sum(stats['avg_shots']) / len(stats['avg_shots']):.1f}" if stats['avg_shots'] else "0",
            'Avg Passes': f"{sum(stats['avg_passes']) / len(stats['avg_passes']):.1f}" if stats['avg_passes'] else "0",
            'Avg Tackles': f"{sum(stats['avg_tackles']) / len(stats['avg_tackles']):.1f}" if stats['avg_tackles'] else "0",
            'Avg Interceptions': f"{sum(stats['avg_interceptions']) / len(stats['avg_interceptions']):.1f}" if stats['avg_interceptions'] else "0",
        }
        for stats in team_stats.values()
    ]
    
    team_quality_columns = [{'name': col, 'id': col} for col in [
        'Team', 'Fixtures Count', 'Complete Data', 'Missing Data', 
        'Missing Statistics', 'Missing Lineups', 'Missing Players'
    ]]
    team_quality_data = [
        {
            'Team': team_stats[team_id]['name'],
            'Fixtures Count': quality['fixtures_count'],
            'Complete Data': quality['complete_data'],
            'Missing Data': quality['missing_data'],
            'Missing Statistics': quality['missing_statistics'],
            'Missing Lineups': quality['missing_lineups'],
            'Missing Players': quality['missing_players'],
        }
        for team_id, quality in team_quality.items()
    ]
    
    team_report_columns = [{'name': col, 'id': col} for col in team_report.columns]
    team_report_data = team_report.to_dict('records')
    
    return (
        team_stats_columns, team_stats_data,
        team_quality_columns, team_quality_data,
        team_report_columns, team_report_data
    )