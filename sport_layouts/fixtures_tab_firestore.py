from dash import dcc, html  # Add both dash components
# If you need more specific components, you can import them like:
# from dash.dependencies import Input, Output, State
def create_data_collection_tab():
    return dcc.Tab(
        label='Data Collection',
        value='data-collection-tab',
        children=[
            # Status store and interval
            dcc.Store(id='status-store'),
            dcc.Interval(
                id='interval-component',
                interval=1*1000,  # 1 second refresh
                n_intervals=0
            ),
            html.Div([
                # Selectors row
                html.Div([
                    html.Div([
                        html.Label('Country'),
                        dcc.Dropdown(
                            id='country-selector',
                            placeholder='Select country...'
                        )
                    ], className='four columns'),
                    html.Div([
                        html.Label('League'),
                        dcc.Dropdown(
                            id='league-selector',
                            placeholder='Select league...',
                        )
                    ], className='four columns'),
                    html.Div([
                        html.Label('Season'),
                        dcc.Dropdown(
                            id='season-selector',
                            placeholder='Select season...',
                        )
                    ], className='four columns'),
                ], className='row'),

                # Collection controls
                html.Div([
                    html.Button(
                        'Collect Fixtures Data',
                        id='collect-data-button',
                        className='button-primary'
                    ),
                ], style={'margin-top': '20px'}),

                # Status and Progress Section
                html.Div([
                    html.Div([
                        html.H4('Collection Status'),
                        html.Div(id='collection-status', style={'fontWeight': 'bold'}),
                        html.Div(id='progress-display'),
                        html.Div(id='error-display', style={'color': 'red'})
                    ]),
                    html.Div([
                        html.H4('Progress Log'),
                        html.Div(
                            id='progress-log',
                            style={
                                'maxHeight': '300px',
                                'overflowY': 'auto',
                                'padding': '10px',
                                'border': '1px solid #ddd',
                                'borderRadius': '5px',
                                'backgroundColor': '#f9f9f9',
                                'fontFamily': 'monospace'
                            }
                        )
                    ], style={'marginTop': '20px'})
                ], style={'margin-top': '20px'})
            ])
        ]
    )