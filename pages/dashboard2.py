
import dash
from dash import html

dash.register_page(__name__, path='/dashboard2')

layout = html.Div([
    html.H1('Dashboard 2'),
    html.P('Visualizações e análises do Dashboard 2.')
])
