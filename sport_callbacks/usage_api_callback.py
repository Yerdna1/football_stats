from dash.dependencies import Input, Output

def setup_usage_api_callbacks(app, api):   
    @app.callback(
        Output('api-usage-display', 'children'),
        Input('interval-component', 'n_intervals')
    )
    def update_api_usage(_):
        usage = api.fetch_api_usage()
        return f"{usage['current']} / {usage['limit_day']} requests"