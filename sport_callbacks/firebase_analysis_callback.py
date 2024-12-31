from dash.dependencies import Input, Output
from dash import html, ctx
from dash.exceptions import PreventUpdate
from sport_analyzers.firebase_analyzer import (
    analyze_data_quality,
    analyze_team_statistics,
    create_data_quality_report,
    create_player_statistics,
    create_player_statistics_table,

    create_team_analysis_report
)
from sport_analyzers.firebase_cache_read import FirebaseCache


def get_fixtures_with_cache(db, cache: FirebaseCache) -> list:
    """
    Get fixtures with caching
    
    Args:
        db: Firebase database instance
        cache: FirebaseCache instance
    """
    # Try to get cached data first
    cached_data = cache.get_cached_data('fixtures')
    if cached_data is not None:
        print("Using cached fixtures data")
        return cached_data
        
    # If no cache, fetch from Firebase
    print("Fetching fresh fixtures data from Firebase")
    fixtures = db.collection('fixtures').stream()
    fixtures_data = [fixture.to_dict() for fixture in fixtures]
    
    # Update cache
    cache.update_cache('fixtures', fixtures_data)
    
    return fixtures_data


def setup_firebase_analysis_callbacks(app, db):
   # Initialize cache with 1-hour duration
   cache = FirebaseCache(cache_duration=21600)
   
   @app.callback(
       [Output('data-quality-container', 'children'),
        Output('player-stats-container', 'children'),
        Output('team-stats-container', 'children'),
        Output('cache-info', 'children')], 
       [Input('analyze-data-button', 'n_clicks'),
        Input('force-refresh-button', 'n_clicks')],
       prevent_initial_call=True
   )
   def update_analysis(n_clicks, refresh_clicks):
       if not n_clicks and not refresh_clicks:
           raise PreventUpdate
       
       print("Starting Firebase data fetch...")
       
       # Check if db connection exists
       if not db:
           print("No Firebase connection!")
           return ["No Firebase connection"] * 4
           
       # Try to get collection reference
       fixtures_ref = db.collection('fixtures')
       if not fixtures_ref:
           print("Cannot access fixtures collection!")
           return ["Cannot access fixtures collection"] * 4
       
       try:
           # Check which button was clicked
           button_id = ctx.triggered[0]['prop_id'].split('.')[0]
           
           # Clear cache if force refresh button was clicked
           if button_id == 'force-refresh-button':
               print("Force refreshing data...")
               cache.clear_cache('fixtures')
           
           # Get fixtures using cache
           fixtures_data = get_fixtures_with_cache(db, cache)
           print(f"Retrieved {len(fixtures_data)} fixtures")

           if not fixtures_data:
               print("No fixtures data found!")
               return ["No fixtures data found in database"] * 4
           
           # Get cache info
           cache_info = cache.get_cache_info('fixtures')
           cache_status = html.Div([
               html.H4("Cache Status", className='text-lg font-semibold mb-2'),
               html.P([
                   "Data Age: ",
                   html.Span(
                       f"{cache_info['age'].total_seconds() / 60:.1f} minutes" 
                       if cache_info['exists'] else "No cache"
                   )
               ]),
               html.P([
                   "Expires in: ",
                   html.Span(
                       f"{cache_info['expires_in'].total_seconds() / 60:.1f} minutes"
                       if cache_info['exists'] else "N/A"
                   )
               ]),
               html.P(f"Cached Records: {cache_info.get('count', 0)}")
           ], className='mt-4 p-4 bg-gray-50 rounded')
           
           # Process data quality
           quality_stats = analyze_data_quality(fixtures_data)
           quality_report = create_data_quality_report(quality_stats)
           
           # Process player statistics
           player_stats = create_player_statistics(fixtures_data)
           player_table = create_player_statistics_table(player_stats)
           
           # Process team statistics
           team_stats, team_quality = analyze_team_statistics(fixtures_data)
           team_report = create_team_analysis_report(team_stats, team_quality)
           
           return quality_report, player_table, team_report, cache_status
           
       except Exception as e:
           print(f"Error in analysis: {e}")
           return (
               html.Div(f"Error: {str(e)}"),
               html.Div("Error loading player stats"),
               html.Div("Error loading team stats"),
               html.Div("Error getting cache info")
           )
