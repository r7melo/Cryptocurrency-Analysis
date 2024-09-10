import dash
from dash import html

dash.register_page(__name__, path='/backtest1')

layout = html.Div([
    html.H1('BACKTEST 01')
])
