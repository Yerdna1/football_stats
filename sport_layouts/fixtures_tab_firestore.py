from dash import dcc, html  # Add both dash components
# If you need more specific components, you can import them like:
# from dash.dependencies import Input, Output, State
def create_selection_row(index):
    return html.Div([
        html.Div([
            html.Label('Country'),
            dcc.Dropdown(
                id={'type': 'country-selector', 'index': index},
                placeholder='Select country...'
            )
        ], className='four columns'),
        html.Div([
            html.Label('League'),
            dcc.Dropdown(
                id={'type': 'league-selector', 'index': index},
                placeholder='Select league...',
            )
        ], className='four columns'),
        html.Div([
            html.Label('Season'),
            dcc.Dropdown(
                id={'type': 'season-selector', 'index': index},
                placeholder='Select season...',
                value='2024',
            )
        ], className='four columns'),
    ], className='row selection-row', id={'type': 'selection-row', 'index': index})


def create_data_collection_tab():
    return dcc.Tab(
        label='Data Collection',
        value='data-collection-tab',
        children=[
            # Status store and interval
            dcc.Store(id='status-store'),
            dcc.Store(id='rows-store', data={'num_rows': 1}),
            dcc.Interval(
                id='interval-component',
                interval=1*1000,  # 1 second refresh
                n_intervals=0
            ),
            html.Div([
                # Container for selection rows
                html.Div(id='selection-rows-container', children=[
                    create_selection_row(0)
                ]),
                
                # Add Row Button
                html.Div([
                    html.Button(
                        '+ Add Selection',
                        id='add-row-button',
                        className='button',
                        style={'marginTop': '10px'}
                    ),
                ], style={'textAlign': 'right'}),

                # Collection controls
                html.Div([
                    html.Button(
                        'Collect Fixtures Data from API and store to Firestore',
                        id='collect-data-button',
                        className='button-primary',
                        disabled=True
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