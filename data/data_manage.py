import os
import pandas as pd
import vectorbt as vbt
import requests
import asyncio
from tqdm.asyncio import tqdm_asyncio
import xml.etree.ElementTree as ET
import yfinance as yf
from datetime import datetime, timedelta

def const_list(path):
    try:
        with open(path, "r", encoding='utf-8') as file:
            return [l.strip() for l in file.read().split('\n')]
    except:
        return []

DATABSE_COINS_PATH = './data/'
CRIPTO_COINS_PATH = './data/cripto/'
FOREX_COINS_PATH = './data/forex/'
CRIPTO_COINS_LIST = const_list('./data/CRIPTO-COINS.txt')
FOREX_COINS_LIST = const_list('./data/FOREX-COINS.txt')
TIME_EXPIRATION = '15m'


class Coin:
    def __init__(self, name) -> None:
        self.name = name

        if name in CRIPTO_COINS_LIST:
            self.context = 'CRIPTO'
            self.path = f'{DATABSE_COINS_PATH}cripto/{TIME_EXPIRATION}/{name}.csv'
            self.dir = f'{DATABSE_COINS_PATH}cripto/{TIME_EXPIRATION}/'
        elif name in FOREX_COINS_LIST:
            self.context = 'FOREX'
            self.path = f'{DATABSE_COINS_PATH}forex/{TIME_EXPIRATION}/{name}.csv'
            self.dir = f'{DATABSE_COINS_PATH}forex/{TIME_EXPIRATION}/'

    def get_df(self, interval=None):
        try:
            if interval is None:
                return pd.read_csv(self.path , index_col=0, parse_dates=True)
            else:
                if self.context == 'FOREX':
                    interval_path = f'{DATABSE_COINS_PATH}forex/{interval}/{self.name}.csv'
                    return pd.read_csv(self.path , index_col=0, parse_dates=True)
        except:
            return []
        
class CoinManage:
    @staticmethod
    def get_coin_list(context) -> list[Coin]:
        coins = []
        try:
            if context == 'CRIPTO':

                for file in os.listdir(CRIPTO_COINS_PATH+TIME_EXPIRATION):
                    name, _ = os.path.splitext(file)
                    coins.append(Coin(name))

            elif context == 'FOREX':

                for file in os.listdir(FOREX_COINS_PATH+TIME_EXPIRATION):
                    name, _ = os.path.splitext(file)
                    coins.append(Coin(name))      

            return coins
        
        except:
            print("Falha ao acessar o diretórios de arquivos")
            return []
    
    @staticmethod
    def get_usdt_cripto_pairs() -> list[str]:

        url = "https://fapi.binance.com/fapi/v1/exchangeInfo" 
        response = requests.get(url)
        data = response.json()

        usdt_pairs = []
        for symbol_info in data['symbols']:
            if symbol_info['quoteAsset'] == 'USDT': 
                usdt_pairs.append(symbol_info['symbol'])

        return usdt_pairs
    
    @staticmethod
    def get_usd_forex_pairs() -> list[str]:

        url = 'https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml'
        response = requests.get(url)
        pares_usd = []
        if response.status_code == 200:
            tree = ET.ElementTree(ET.fromstring(response.content))
            root = tree.getroot()
            for cube in root.findall('.//{*}Cube[@currency]'):
                currency = cube.get('currency')
                if currency != 'USD':
                    pares_usd.append(f'{currency}USD')
        else:
            print("Falha ao obter dados:", response.status_code)

        return pares_usd
    
    @staticmethod
    def download_coin(coin:Coin, start):

        if coin.context == 'CRIPTO':
            try:
                cripto_data = vbt.BinanceData.download(
                    coin.name,
                    start=start, 
                    end='now UTC',
                    interval=TIME_EXPIRATION
                )

                return cripto_data.get()
            
            except Exception as e:
                print(f'Falha ao baixar {coin.name} - CRIPTO')
                print(e)
                return []
        
        elif coin.context == 'FOREX':
            try:
                return yf.download(coin.name+'=X', interval=TIME_EXPIRATION, start=start)
            except:
                print(f'Falha ao baixar {coin.name} - FOREX')
                return []

        
    @staticmethod
    def update_coin(coin:Coin):
        if coin.context == 'CRIPTO':
            start_cripto = '7 day ago UTC'

            try:
                data = coin.get_df()
                start_cripto = data.index[-1]

                df_new = CoinManage.download_coin(coin, start_cripto)

                data = pd.concat([data.iloc[:-1], df_new])
                data.to_csv(coin.path)

            except:
                
                data = CoinManage.download_coin(coin, start_cripto)

                if len(data) > 1:
                    data.to_csv(coin.path)

        elif coin.context == 'FOREX':
            start_forex = (datetime.now() - timedelta(days=50)).strftime('%Y-%m-%d')

            try:
                
                data = coin.get_df()
                start_forex = data.index[-1]
                start_forex = start_forex.strftime('%Y-%m-%d')

                df_new = CoinManage.download_coin(coin, start_forex)

                df_concatenado = pd.concat([data, df_new]).sort_index().drop_duplicates(keep='last')

                df_concatenado.to_csv(coin.path)

            except:
                
                df_new = CoinManage.download_coin(coin, start_forex)

                if len(df_new) > 1:
                    df_new.to_csv(coin.path)

    @staticmethod
    def upgrade_all_coins_async(coins_list):
        asyncio.run(CoinManage()._download_progress_bar(coins_list))

    async def _download_async(self, coin_name):
        coin = Coin(coin_name)
        await asyncio.to_thread(CoinManage.update_coin, coin)

    async def _download_progress_bar(self, coins_list):
        tasks = [self._download_async(coin_name) for coin_name in coins_list]
        for f in tqdm_asyncio.as_completed(tasks, total=len(tasks), desc="Baixando dados das moedas"):
            await f

    @staticmethod
    def upgrade_all_coins_sync(coins_list):
        for coin_name in coins_list:
            coin = Coin(coin_name)
            CoinManage.update_coin(coin)

if __name__=='__main__':
   # CoinManage.upgrade_all_coins_async(CRIPTO_COINS_LIST) 
    CoinManage.upgrade_all_coins_sync(FOREX_COINS_LIST) 