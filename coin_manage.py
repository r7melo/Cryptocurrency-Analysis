import os
import pandas as pd
import vectorbt as vbt
import requests
import asyncio
from tqdm.asyncio import tqdm_asyncio

COIN_BASE_PATH = 'C:/CoinsBase/1h/{}.csv'

class Coin:
    def __init__(self, name="BTCUSDT") -> None:
        self.name = name
        self.path = COIN_BASE_PATH.format(name)
        
    def get_df(self):
        return pd.read_csv(self.path , index_col=0, parse_dates=True)

class CoinManage:
    @staticmethod
    def get_coin_list() -> list[Coin]:
        coins = []
        try:
            for file in os.listdir('C:/CoinsBase/1h/'):
                name, _ = os.path.splitext(file)
                coins.append(
                    Coin(name)
                )        
        except:
            print("Falha ao acessar a lista de símbolos.")

        return coins
    
    @staticmethod
    def get_usdt_futures_pairs() -> list[str]:

        url = "https://fapi.binance.com/fapi/v1/exchangeInfo" 
        response = requests.get(url)
        data = response.json()

        usdt_pairs = []
        for symbol_info in data['symbols']:
            if symbol_info['quoteAsset'] == 'USDT': 
                usdt_pairs.append(symbol_info['symbol'])

        return usdt_pairs
    
    @staticmethod
    def download_coin(coin:Coin, start):
        try:
            binance_data = vbt.BinanceData.download(
                coin.name,
                start=start, 
                end='now UTC',
                interval='1h',

            )

            return binance_data.get()
        
        except:
            print(f'Falha ao baixar {coin.name}')
            return []
        
    @staticmethod
    def update_coin(coin:Coin):
        start = '7 day ago UTC'

        try:
            data = coin.get_df()
            start = data.index[-1]

            df_new = CoinManage.download_coin(coin, start)

            data = pd.concat([data.iloc[:-1], df_new])
            data.to_csv(coin.path)

        except:
            
            data = CoinManage.download_coin(coin, start)

            if len(data) > 1:
                data.to_csv(coin.path)

    @staticmethod
    def upgrade_all_coins():
        coins_list = CoinManage.get_usdt_futures_pairs()
        asyncio.run(CoinManage()._download_progress_bar(coins_list))

    async def _download_async(self, coin_name):
        await asyncio.to_thread(CoinManage.update_coin, Coin(coin_name))

    async def _download_progress_bar(self, coins_list):
        tasks = [self._download_async(coin_name) for coin_name in coins_list]
        for f in tqdm_asyncio.as_completed(tasks, total=len(tasks), desc="Baixando dados das moedas"):
            await f

    

if __name__=='__main__':
    CoinManage.upgrade_all_coins()