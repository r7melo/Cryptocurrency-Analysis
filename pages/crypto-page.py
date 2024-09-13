import dash
import pandas as pd
import numpy as np
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import dcc, html, Output, Input, callback
from classes.crypto_coin import CryptoCoin
from classes.indicators import Indicator
from classes.backtests import BackTest
from components.graph import GraphComponent
from utils.center_of_force import center_of_force
from classes.logger import Logger




def construct_averages(df: pd.DataFrame) -> pd.DataFrame:

    df['Center'] = center_of_force(df['High'], df['Open'], df['Close'], df['Low'])
    df['EMA_9'] =  Indicator.exponential_mean(df['Center'], 9)
    df['EMA_21'] =  Indicator.exponential_mean(df['Center'], 21)
    df['EMA_34'] = Indicator.exponential_mean(df['Center'], 34)
    df['EMA_72'] = Indicator.exponential_mean(df['Center'], 72)
    df['EMA_305'] = Indicator.exponential_mean(df['Center'], 305)

    return df


def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:

    Indicator.detect_highs_and_lows(df, window=2) # adiciona no df a coluna 'High_Low'
    Indicator.cut_candle(df, 'EMA_9') #  # adiciona no df a coluna 'EMA_9_Cut_Candle'


    filter_approximate_EMAs = Indicator.approximate_values(df, columns=['EMA_9', 'EMA_21'], tolerance=0.0005)
    df['Approximate_EMAs'] = df.loc[filter_approximate_EMAs, 'EMA_34']

    # filter_tendence_sell = Indicator.check_tendence(df, columns=['EMA_9', 'EMA_305'], ascending=True) # < 
    # filter_tendence_buy = Indicator.check_tendence(df, columns=['EMA_9', 'EMA_305' ], ascending=False) # >

    filter_body_candle = Indicator.largest_candle_body_sum(df, 2)
    filter_opposite_candle = Indicator.is_opposite_candle(df)
    filter_shift_is_ind = df['EMA_9_Cut_Candle'].shift(1).notna()

    teste = df['Low'].shift(2).rolling(window=2).min() > df['Low']
    teste2 = df['High'].shift(2).rolling(window=2).max() < df['High']


    f = filter_body_candle # & (teste | teste2)
    

    df['Indicador_Setup'] = np.nan
    df['Indicador_Setup'] = df.loc[f, 'EMA_9_Cut_Candle']
    
   

    #df.to_csv('./monitoring.csv')


    
    return df




def update_graph():

    coin = CryptoCoin('BTCUSDT')
    coin.path = './data/crypto/1h/BTCUSDT.csv'
    #coin.update()
    
    df = coin.get_dataframe()

    df = construct_averages(df)
    df = calculate_indicators(df)

    df, feedbackS91 = BackTest.backtest_setup_by_indicator(df, period=16, indicator_name='EMA_9_Cut_Candle')
    df['EMA_9_Cut_Candle_Operation_Gain'] = df.loc[ df['EMA_9_Cut_Candle_Operation'] == 'Gain', 'Center']
    df['EMA_9_Cut_Candle_Operation_Loss'] = df.loc[ df['EMA_9_Cut_Candle_Operation'] == 'Loss', 'Center']

    df, feedbackInd = BackTest.backtest_setup_by_indicator(df, period=16, indicator_name='Indicador_Setup')
    df['Indicador_Setup_Operation_Gain'] = df.loc[ df['Indicador_Setup_Operation'] == 'Gain', 'Center']
    df['Indicador_Setup_Operation_Loss'] = df.loc[ df['Indicador_Setup_Operation'] == 'Loss', 'Center']
     
    # Renderizar somente os ultimos 900 candles
    df = df[-500:]

    candlestick = lambda name, df: go.Candlestick( x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='Candlestick')
    line = lambda name, color, dfy: go.Scatter( x=df.index, y=dfy, mode='lines', name=name, line=dict(color=color), visible='legendonly')
    marker = lambda name, color, dfy: go.Scatter( x=df.index, y=dfy, mode='markers', name=name, marker=dict(color=color, size=10), visible='legendonly')

    # Gráfico de Candlestick
    fig = GraphComponent.get_figure()
    fig.update_layout(title=coin.name)

    fig.add_trace(go.Scatter(x=df.index, y=df['High_Low'], mode='lines', name='High_Low', line=dict(color='rgba(255,255,255,0.5)')), row=1, col=1)
    fig.add_trace(candlestick('Candlestick', df), row=1, col=1)

    # Adicionando EMAs
    fig.add_trace(line('EMA 9', '#1ff', df['EMA_9']), row=1, col=1)
    fig.add_trace(line('EMA 21', '#1bf', df['EMA_21']), row=1, col=1)
    fig.add_trace(line('EMA 34', '#fbcfb7', df['EMA_34']), row=1, col=1)
    fig.add_trace(line('EMA 72', '#f8ae86', df['EMA_72']), row=1, col=1)
    fig.add_trace(line('EMA 305', '#f58e56', df['EMA_305']), row=1, col=1)




    fig.add_trace(marker(f'34x72x305', '#1b98e0', df['Approximate_EMAs'] ), row=1, col=1)





    # Backtest FeedBack
    fig.add_trace(marker(f'S9.1 LOSS ({feedbackS91['Loss%']:.0f}% - {feedbackS91['Loss']} ent.)', '#f00', df['EMA_9_Cut_Candle_Operation_Loss'] ), row=1, col=1)
    fig.add_trace(marker(f'S9.1 GAIN ({feedbackS91['Gain%']:.0f}% - {feedbackS91['Gain']} ent.)', '#0f0', df['EMA_9_Cut_Candle_Operation_Gain'] ), row=1, col=1)

    fig.add_trace(marker(f'Ind. LOSS ({feedbackInd['Loss%']:.0f}% - {feedbackInd['Loss']} ent.)', '#f00', df['Indicador_Setup_Operation_Loss'] ), row=1, col=1)
    fig.add_trace(marker(f'Ind. GAIN ({feedbackInd['Gain%']:.0f}% - {feedbackInd['Gain']} ent.)', '#0f0', df['Indicador_Setup_Operation_Gain'] ), row=1, col=1)


    return fig




# Registra a página
dash.register_page(__name__, path='/crypto-page')

# Layout da página
layout = dbc.Container(
    [
        dbc.Row(
            [
                # GRAPH COIN
                dcc.Graph(id='graph-crypto', figure=GraphComponent.get_figure(), style={'height': '100%', 'width': '100%'}, config={'responsive': True} ),
                html.Button('Update Price', id='button-update-crypto', n_clicks=0)
            ]
        ),
        dcc.Store(id='store', data={'updated': False}),


        dcc.Interval( id='interval-component',  interval=10000000, n_intervals=0)
    ], 
    fluid=True
)

@callback(
    Output('graph-crypto', 'figure'),
    Input('button-update-crypto', 'n_clicks'),
    prevent_initial_call=False
)
def update_data(n_clicks):

    try:
        return update_graph()
    except Exception as ex:
        Logger.log("Erro ao atualizar o gráfico: ", ex)
        return GraphComponent.get_figure() 






