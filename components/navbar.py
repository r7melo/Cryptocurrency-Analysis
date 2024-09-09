# components/navbar.py
from dash import html, dcc

# Componente de navegação
navbar = html.Div([
    dcc.Link('Dashboard 1', href='/dashboard1', className='nav-link'),
    html.Span(' | ', className='nav-separator'),
    dcc.Link('Dashboard 2', href='/dashboard2', className='nav-link'),
    html.Span(' | ', className='nav-separator'),
    dcc.Link('Backtest 1', href='/backtest1', className='nav-link'),
    html.Span(' | ', className='nav-separator'),
    dcc.Link('Backtest 2', href='/backtest2', className='nav-link'),
], className='navbar')
