# Table styles
table_cell_style = {
    'textAlign': 'left',
    'padding': '10px',
    'whiteSpace': 'normal',
    'height': 'auto',
    'width': '20px',
    'font-family': 'Arial, sans-serif',
    'fontSize': '14px'
}

table_header_style = {
    'backgroundColor': 'rgb(230, 230, 230)',
    'fontWeight': 'bold',
    'borderBottom': '2px solid rgb(200, 200, 200)'
}

table_style = {
    'margin': '20px auto',
    'width': '90%',
    'boxShadow': '0 0 5px rgba(0,0,0,0.1)',
    'borderRadius': '5px',
    'tableLayout': 'fixed'
}

table_conditional_style = [
    {
        'if': {'row_index': 'odd'},
        'backgroundColor': 'rgb(248, 248, 248)'
    }
]