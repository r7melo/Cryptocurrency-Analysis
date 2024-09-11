import dash
import pandas as pd
import numpy as np
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import dcc, html, Output, Input, callback
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

# Função para capturar uma página específica do DataFrame
def get_page(df, page_number, chunk_size=1000):
    total_rows = len(df)
    if page_number < 1 or (page_number - 1) * chunk_size >= total_rows:
        print(f"Página {page_number} está fora do intervalo. Total de linhas é {total_rows}.")
        return
    
    # Calcula os índices de início e fim com base na página
    start = total_rows - page_number * chunk_size
    end = total_rows - (page_number - 1) * chunk_size
    start = max(start, 0)  # Garante que o índice de início não seja menor que 0
    
    # Seleciona o bloco de dados
    chunk = df[start:end]
    return chunk

def update_graph_forex():

    coin = ForexCoin('EURUSD')
    coin.path = './data/forex/15m/EURUSD.csv'
    
    coin.update()
    
    df = coin.get_dataframe()


    df = get_page(df, 6)
    df = calculate_indicators(df)

    candlestick = lambda name, df: go.Candlestick( x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='Candlestick')
    line = lambda name, color, dfy: go.Scatter( x=df.index, y=dfy, mode='lines', name=name, line=dict(color=color), visible='legendonly')
    marker = lambda name, color, dfy: go.Scatter( x=df.index, y=dfy, mode='markers', name=name, marker=dict(color=color, size=10), visible='legendonly')
    
    # Renderizar somente os ultimos 900 candles
    df = df[-500:]

    # Gráfico de Candlestick
    fig = GraphComponent.get_figure()
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

# Layout da página
layout = dbc.Container(
    [
        dbc.Row(
            [
                # GRAPH COIN
                dcc.Graph(id='graph-forex', figure=GraphComponent.get_figure()),
                html.Button('Update Price', id='button-update-forex', n_clicks=0)
            ]
        ),
        dcc.Store(id='store', data={'updated': False})
    ], 
    fluid=True
)

@callback(
    Output('graph-forex', 'figure'),
    Input('button-update-forex', 'n_clicks'),
    prevent_initial_call=False
)
def update_data(n_clicks):

    try:
        return update_graph_forex()
    except Exception as e:
        return GraphComponent.get_figure() 






