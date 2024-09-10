
import dash
from dash import html

dash.register_page(__name__, path='/crypto-page')

layout = html.Div([
    html.H1('Crypto'),
    html.P('Visualizações e análises das criptomoedas.')
])
