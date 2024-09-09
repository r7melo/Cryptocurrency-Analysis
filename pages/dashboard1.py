# pages/dashboard1.py
import dash
from dash import html

# Registra a página
dash.register_page(__name__, path='/dashboard1')

# Layout da página do Dashboard 1
layout = html.Div([
    html.H1('Dashboard 1'),
    html.P('Visualizações e análises do Dashboard 1.')
])
