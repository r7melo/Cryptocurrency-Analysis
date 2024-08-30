import os
import pandas as pd
import vectorbt as vbt

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
    def download_coin(coin:Coin, start):
        try:
            binance_data = vbt.BinanceData.download(
                coin.name,
                start=start, 
                end='now UTC',
                interval='1h'
            )

            return binance_data.get()
        
        except:
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
            print(f"{coin.name} - Arquivo local atualizado.")

        except:
            
            data = CoinManage.download_coin(coin, start)

            if len(data) > 1:
                data.to_csv(coin.path)
                print(f"{coin.name} - Arquivo local gerado.")
