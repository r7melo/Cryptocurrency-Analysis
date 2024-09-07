from coin_manage import CoinManage, Coin
import asyncio
from tqdm.asyncio import tqdm_asyncio
import numpy as np
from dash import Dash, html, dash_table
import pandas as pd
import dash_bootstrap_components as dbc

async def backtest(coin:Coin):

    df = await asyncio.to_thread(coin.get_df)
    score = 0
    direction = '--'
    distance = 0
    
    #region BACKTEST

    df['EMA_9'] = ((df['Close']+df['Open'])/2).ewm(span=9, adjust=False).mean()
    shift24 = df['EMA_9'].shift(-9)

    df['SMA_10'] = df['Close'].rolling(window=10).mean() 
    df['SMA_15'] = df['Close'].rolling(window=15).mean()  
    df['SMA_30'] = df['Close'].rolling(window=30).mean()  

    ind_EMA_9_buy = (df['Open'] < df['EMA_9']) & (df['EMA_9'] < df['Close']) & (df['EMA_9'] > df['SMA_10']) & (df['SMA_10'] > df['SMA_15'] ) & (df['SMA_10'] > df['SMA_30'])
    ema9_buy = (df[ind_EMA_9_buy])['EMA_9']

    points_buy = ema9_buy - shift24
    points_buy = points_buy.dropna() 
    p_buy = len(points_buy[points_buy < 0])
    total_buy = len(points_buy)

    score_buy = 0
    if total_buy > 0:
        score_buy = (p_buy/total_buy)*100

    ind_EMA_9_sell = (df['Open'] > df['EMA_9']) & (df['EMA_9'] > df['Close']) & (df['EMA_9'] < df['SMA_10']) & (df['SMA_10'] < df['SMA_15'] ) & (df['SMA_10'] < df['SMA_30'])
    ema9_sell = (df[ind_EMA_9_sell])['EMA_9']
    
    points_sell = ema9_sell - shift24 
    points_sell = points_sell.dropna()
    p_sell = len(points_sell[points_sell > 0])
    total_sell = len(points_sell)

    score_sell = 0
    if score_sell > 0:
        score_sell = (p_sell/total_sell)*100

    pc = (0,0)
    if score_buy > score_sell:
        score = score_buy
        direction = 'Buy'
        pc = (p_buy, total_buy)
        distance = abs(ema9_buy.index[-1] - df['EMA_9'].index[-1]) if len(ema9_buy) > 0 else -1
    else:
        score = score_sell
        direction = 'Sell'
        pc = (p_sell, total_sell)
        distance = abs(ema9_sell.index[-1] - df['EMA_9'].index[-1]) if len(ema9_sell) > 0 else -1

    distance = (distance.total_seconds() / 3600) if distance != -1 else np.nan
    #endregion

    return coin.name, score, direction, pc[0], pc[1], distance

#region PROCESS BACKTEST
async def process_backtest():

    coin_list = CoinManage.get_coin_list()
    backtest_tasks = [backtest(coin) for coin in coin_list]
    backtest_results = await asyncio.gather(*backtest_tasks)
    symbols, score, direction, ac, tac, distance = zip(*backtest_results)
    result_df = pd.DataFrame({
        'Symbol': symbols,
        'Score': score,
        'Direction':direction, 
        'Acertividade':ac, 
        'Total Ac.': tac, 
        'Distance':distance
    })
    return result_df.sort_values(by=['Score','Total Ac.','Distance'], ascending=[False, False, True])

def feedback_backtest():

    async def async_wrapper():
        return await process_backtest()

    return asyncio.run(_download_progress_bar())

async def _download_async(self, coin_name):
        await asyncio.to_thread(CoinManage.update_coin, Coin(coin_name))

async def _download_progress_bar(self, coins_list):
    tasks = [_download_async(coin_name) for coin_name in coins_list]
    for f in tqdm_asyncio.as_completed(tasks, total=len(tasks), desc="Baixando dados das moedas"):
        await f

#endregion

if __name__ == '__main__':

    df = feedback_backtest()

    app = Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])
    app.layout = dbc.Container(
        [
            html.H1("Tabela de Back-Tests"),
            html.Div(
                dash_table.DataTable(
                    id='tabela',
                    columns=[{"name": i, "id": i} for i in df.columns],
                    data=df.to_dict('records'),
                    style_table={
                        'width': '100%',  # Largura fixa
                        'height': '600px',  # Altura fixa
                        'overflowX': 'auto',  # Adiciona rolagem horizontal se necessário
                        'overflowY': 'auto'   # Adiciona rolagem vertical se necessário
                    },
                    style_cell={'textAlign': 'left'},  # Alinha o texto à esquerda
                )
            ),
        ], 
        fluid=True
    )

    app.run(debug=True, port=8052)
""