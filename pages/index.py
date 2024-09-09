# pages/index.py
import dash
from dash import html
from components.navbar import navbar

# Registra a página principal
dash.register_page(__name__, path='/')

# Layout da página principal
layout = html.Div([
    navbar,
    html.Div(id='page-content')  # Container para o conteúdo da página
])
