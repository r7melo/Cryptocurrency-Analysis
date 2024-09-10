# components/navbar.py
from dash import html, dcc

# Componente de navegação
navbar = html.Div([
    dcc.Link('Forex', href='/forex-page', className='nav-link'),
    html.Span(' | ', className='nav-separator'),
    dcc.Link('Crypto', href='/crypto-page', className='nav-link'),
    html.Span(' | ', className='nav-separator'),
    dcc.Link('Backtest 1', href='/backtest1', className='nav-link'),
    html.Span(' | ', className='nav-separator'),
    dcc.Link('Backtest 2', href='/backtest2', className='nav-link'),
], className='navbar')
