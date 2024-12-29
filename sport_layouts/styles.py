# Table styles
table_cell_style = {
    'textAlign': 'left',
    'padding': '10px',
    'whiteSpace': 'pre-line',  # Changed to pre-line to preserve line breaks
    'whiteSpace': 'normal',
    'height': 'auto',
    'maxWidth': '400px',  # Increased for more injury history
    'font-family': 'Arial, sans-serif',
    'fontSize': '14px',
    'overflow': 'hidden',
    'textOverflow': 'ellipsis',
    'lineHeight': '1.4'  # Better spacing for readability
}

table_header_style = {
    'backgroundColor': 'rgb(230, 230, 230)',
    'fontWeight': 'bold',
    'borderBottom': '2px solid rgb(200, 200, 200)',
    'height': 'auto',
    'textAlign': 'center',
    'whiteSpace': 'normal'  # Allows header text to wrap
}

table_style = {
    'margin': '20px auto',
    'width': '98%',  # Increased width to accommodate injury information
    'boxShadow': '0 0 5px rgba(0,0,0,0.1)',
    'borderRadius': '5px',
    'overflowX': 'auto'
}

table_conditional_style = [
    {
        'if': {'row_index': 'odd'},
        'backgroundColor': 'rgb(248, 248, 248)'
    }
]