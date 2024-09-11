import dash
import pandas as pd
import numpy as np
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import dcc
from classes.forex_coin import ForexCoin
from classes.indicator import Indicator
from components.graph import GraphComponent


def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:

    df['Percentual'] = ((df['Close'] - df['Open']) / df['Open']) * 100
    df['MP'] = Indicator.mean(df['Percentual'], 30) * 10

    df['SMA_10'] = Indicator.mean(df['Close'], 10)
    df['SMA_15'] = Indicator.mean(df['Close'], 15)
    df['SMA_30'] = Indicator.mean(df['Close'], 30)

    price_center = ((df['Close']+df['Open'])/2)
    df['EMA_9'] =  Indicator.exponential_mean(price_center, 9)
    

    df_setup_9_1 = Indicator.setup_9_1(df)
    df['_9_1_Buy'] = df_setup_9_1[df_setup_9_1['Setup_9_1'] == 'Buy']['EMA_9']
    df['_9_1_Sell'] = df_setup_9_1[df_setup_9_1['Setup_9_1'] == 'Sell']['EMA_9']

    test = Indicator.setup_test(df)

    df['Gains'] = test[test['Operation'] == 'Gain']['EMA_9'] * 1.001

    return df


def update_graph_forex(fig:go.Figure):
    
    coin = ForexCoin('EURUSD')
    coin.path = './data/forex/15m/EURUSD.csv'

    df = coin.get_dataframe()
    df = calculate_indicators(df)

    candlestick = lambda name, df: go.Candlestick( x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='Candlestick')
    line = lambda name, color, dfy: go.Scatter( x=df.index, y=dfy, mode='lines', name=name, line=dict(color=color), visible='legendonly')
    marker = lambda name, color, dfy: go.Scatter( x=df.index, y=dfy, mode='markers', name=name, marker=dict(color=color, size=10), visible='legendonly')
    
    # Renderizar somente os ultimos 900 candles
    df = df[-500:]

    # Gráfico de Candlestick
    fig.add_trace(candlestick('Candlestick', df), row=1, col=1)

    # Adicionando média móvel
    fig.add_trace(line('SMA 10', '#fbcfb7', df['SMA_10']), row=1, col=1)
    fig.add_trace(line('SMA 15', '#f8ae86', df['SMA_15']), row=1, col=1)
    fig.add_trace(line('SMA 30', '#f58e56', df['SMA_30']), row=1, col=1)
    fig.add_trace(line('EMA 9', '#1bf', df['EMA_9']), row=1, col=1)

    n_setup_9_1_buy, n_setup_9_1_sell = df['_9_1_Buy'].count(), df['_9_1_Sell'].count()
    fig.add_trace(marker(f'SETUP 9.1 BUY ({n_setup_9_1_buy})', '#fff', df['_9_1_Buy']), row=1, col=1)
    fig.add_trace(marker(f'SETUP 9.1 SELL ({n_setup_9_1_sell})', '#fff', df['_9_1_Sell']), row=1, col=1)

    percentage_gain = df['Percentage_Gain'].iloc[0]
    fig.add_trace(marker(f'GAIN ({percentage_gain:.0f}%)', '#0f0', df['Gains']), row=1, col=1)

    return fig




# Registra a página
dash.register_page(__name__, path='/forex-page')

graph_component = GraphComponent('forex')

# Layout da página
layout = dbc.Container(
    [
        dbc.Row(
            [
                # GRAPH COIN
                graph_component.graph
            ]
        ),
        
    ], 
    fluid=True
)

graph_component.init_callback(dash.get_app())
graph_component.fig = update_graph_forex(graph_component.fig)