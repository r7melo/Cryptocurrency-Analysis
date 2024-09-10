import dash
import pandas as pd
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import Input, Output, html, dcc, callback
from classes.forex_coin import ForexCoin
from classes.indicator import Indicator

# Registra a página
dash.register_page(__name__, path='/forex-page')

# Layout da página
layout = dbc.Container(
    [
        dbc.Row(
            [
                # GRAPH COIN
                dcc.Graph(id='graph-forex'),
                dcc.Interval(
                    id='interval-graph-forex',
                    interval=5*60*1000, # 5 min
                    n_intervals=0
                ),
            ]
        ),
        
    ], 
    fluid=True
)


@callback(
    Output('graph-forex', 'figure'),
    Input('interval-graph-forex', 'n_intervals')
)
def update_graph_forex(n):
    
    coin = ForexCoin('EURUSD')
    coin.path = './data/forex/15m/EURUSD.csv'

    df = coin.get_dataframe()[-900:]

    df['Percentual'] = ((df['Close'] - df['Open']) / df['Open']) * 100
    df['MP'] = Indicator.mean(df['Percentual'], 30) * 10

    df['SMA_10'] = Indicator.mean(df['Close'], 10)
    df['SMA_15'] = Indicator.mean(df['Close'], 15)
    df['SMA_30'] = Indicator.mean(df['Close'], 30)

    price_center = ((df['Close']+df['Open'])/2)
    df['EMA_9'] =  Indicator.exponential_mean(price_center, 9)


    df['LOSS_BUY'] = (df['Low'].shift(-9).rolling(window=9).min()).shift(9)
    df['LOSS_SELL'] = (df['High'].shift(-9).rolling(window=9).max()).shift(9)

    # Criando subplots
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1, row_heights=[.9, .1])

    candlestick = lambda name, df: go.Candlestick( x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='Candlestick')
    scatter = lambda name, color, dfy: go.Scatter( x=df.index, y=dfy, mode='lines', name=name, line=dict(color=color), visible='legendonly')
    # Gráfico de Candlestick
    fig.add_trace(candlestick('Candlestick', df), row=1, col=1)

    # Adicionando média móvel
    fig.add_trace(scatter('SMA 10', '#fbcfb7', df['SMA_10']), row=1, col=1)
    fig.add_trace(scatter('SMA 15', '#f8ae86', df['SMA_15']), row=1, col=1)
    fig.add_trace(scatter('SMA 30', '#f58e56', df['SMA_30']), row=1, col=1)
    fig.add_trace(scatter('LOSS BUY', '#030', df['LOSS_BUY']), row=1, col=1)
    fig.add_trace(scatter('LOSS SELL', '#300', df['LOSS_SELL']), row=1, col=1)
    fig.add_trace(scatter('EMA 9', '#1bf', df['EMA_9']), row=1, col=1)


    fig.update_layout(
        title=dict(
            text=coin.name,
            font=dict(size=20, color='white')  # Cor e tamanho do título
        ),
        xaxis=dict(
            title='Tempo',  # Título do eixo x
            title_font=dict(size=14, color='white'),  # Cor e tamanho do título do eixo x
            type='date',  # Define o tipo de dado como data
            tickformat='%d-%m-%Y %H:%M',  # Formato dos ticks para o eixo de tempo
            tickfont=dict(color='lightgray'),  # Cor das marcações dos ticks
            tickangle=45,  # Ângulo dos ticks para melhor visualização
            gridcolor='gray',  # Cor das linhas de grade verticais
            showline=True,  # Mostra a linha do eixo x
            linecolor='white',  # Cor da linha do eixo x
        ),
        yaxis=dict(
            title='Price',  # Título do eixo y
            title_font=dict(size=14, color='white'),  # Cor e tamanho do título do eixo y
            tickfont=dict(color='lightgray'),  # Cor das marcações dos ticks no eixo y
            gridcolor='gray',  # Cor das linhas de grade horizontais
            showline=True,  # Mostra a linha do eixo y
            linecolor='white',  # Cor da linha do eixo y
        ),
        template='plotly_dark',  # Tema escuro
        height=900,
        legend=dict(
            orientation='h',
            bgcolor='rgba(0,0,0,0.5)',
            bordercolor='white',
            borderwidth=1,
            font=dict(
                size=12,
                color='white'
            )
        )
    )


    return fig
