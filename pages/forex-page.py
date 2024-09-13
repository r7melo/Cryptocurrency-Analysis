import dash
import pandas as pd
import numpy as np
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import dcc, html, Output, Input, callback
from classes.forex_coin import ForexCoin
from classes.indicators import Indicator
from classes.backtests import BackTest
from components.graph import GraphComponent
from utils.center_of_force import center_of_force
from classes.logger import Logger





def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:

    df['Center'] = center_of_force(df['High'], df['Open'], df['Close'], df['Low'])

    Indicator.detect_highs_and_lows(df, window=5)
    df['High_Low'] = np.nan
    df.loc[df['Peak_High'], 'High_Low'] = df['High']
    df.loc[df['Trough_Low'], 'High_Low'] = df['Low']
    df['High_Low'] = df['High_Low'].interpolate(method='linear')

    df['EMA_9'] =  Indicator.exponential_mean(df['Center'], 9)
    df['EMA_21'] =  Indicator.exponential_mean(df['Center'], 21)
    df['EMA_34'] = Indicator.exponential_mean(df['Center'], 34)
    df['EMA_72'] = Indicator.exponential_mean(df['Center'], 72)
    df['EMA_305'] = Indicator.exponential_mean(df['Center'], 305)

    df = Indicator.cut_candle(df, 'EMA_9')

    filter_approximate_EMAs = Indicator.approximate_values(df, columns=['EMA_34', 'EMA_72', 'EMA_305'], tolerance=0.00005)
    df['Approximate_EMAs'] = df.loc[filter_approximate_EMAs, 'Center']

    indicado_sell = (filter_approximate_EMAs) | (df['EMA_9_Cut_Candle'] == 'Sell')
    indicado_buy = (filter_approximate_EMAs) | (df['EMA_9_Cut_Candle'] == 'Buy')

    df['Indicador_Setup'] = pd.Series([np.nan] * len(df), dtype='object')
    df.loc[indicado_sell , 'Indicador_Setup'] = 'Sell'
    df.loc[indicado_buy , 'Indicador_Setup'] = 'Buy'

    df['Indicador'] = df.loc[indicado_sell | indicado_buy, 'EMA_9']

    print(df['Indicador_Setup'].value_counts(), end='\n\n')

    return df




def update_graph_forex():

    coin = ForexCoin('EURUSD')
    coin.path = './data/forex/15m/EURUSD.csv'
    #coin.update()
    
    df = coin.get_dataframe()

    df = calculate_indicators(df)

    df, feedbackEMA9 = BackTest.backtest_setup_by_indicator(df, period=8, indicator_name='Indicador_Setup')
    df['Indicador_Price_Gain'] = df.loc[ df['Indicador_Setup_Operation'] == 'Gain', 'Center']
    df['Indicador_Price_Loss'] = df.loc[ df['Indicador_Setup_Operation'] == 'Loss', 'Center']
     
    # Renderizar somente os ultimos 900 candles
    df = df[-500:]

    candlestick = lambda name, df: go.Candlestick( x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='Candlestick')
    line = lambda name, color, dfy: go.Scatter( x=df.index, y=dfy, mode='lines', name=name, line=dict(color=color), visible='legendonly')
    marker = lambda name, color, dfy: go.Scatter( x=df.index, y=dfy, mode='markers', name=name, marker=dict(color=color, size=10), visible='legendonly')

    # Gráfico de Candlestick
    fig = GraphComponent.get_figure()
    fig.update_layout(title=coin.name)

    fig.add_trace(go.Scatter(x=df.index, y=df['High_Low'], mode='lines', name='High_Low', line=dict(color='white')), row=1, col=1)
    fig.add_trace(candlestick('Candlestick', df), row=1, col=1)

    # Adicionando média móvel
    fig.add_trace(line('EMA 9', '#1ff', df['EMA_9']), row=1, col=1)
    fig.add_trace(line('EMA 21', '#1bf', df['EMA_21']), row=1, col=1)
    fig.add_trace(line('EMA 34', '#fbcfb7', df['EMA_34']), row=1, col=1)
    fig.add_trace(line('EMA 72', '#f8ae86', df['EMA_72']), row=1, col=1)
    fig.add_trace(line('EMA 305', '#f58e56', df['EMA_305']), row=1, col=1)

    fig.add_trace(marker(f'Ind. GAIN ({feedbackEMA9['Gain%']:.0f}% - {feedbackEMA9['Gain']} ent.)', '#0f0', df['Indicador_Price_Gain'] ), row=1, col=1)
    fig.add_trace(marker(f'Ind. LOSS ({feedbackEMA9['Loss%']:.0f}% - {feedbackEMA9['Loss']} ent.)', '#f00', df['Indicador_Price_Gain'] ), row=1, col=1)


    fig.add_trace(marker(f'Approximate EMAs', '#fff',  df['Approximate_EMAs']), row=1, col=1)
    fig.add_trace(marker(f'INDICADOR', '#0ff',  df['Indicador']), row=1, col=1)


    return fig




# Registra a página
dash.register_page(__name__, path='/forex-page')

# Layout da página
layout = dbc.Container(
    [
        dbc.Row(
            [
                # GRAPH COIN
                dcc.Graph(id='graph-forex', figure=GraphComponent.get_figure(), style={'height': '100%', 'width': '100%'}, config={'responsive': True} ),
                html.Button('Update Price', id='button-update-forex', n_clicks=0)
            ]
        ),
        dcc.Store(id='store', data={'updated': False}),


        dcc.Interval( id='interval-component',  interval=10000000, n_intervals=0)
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
    except Exception as ex:
        Logger.log("Erro ao atualizar o gráfico: ", ex)
        return GraphComponent.get_figure() 






