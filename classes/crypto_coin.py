import vectorbt as vbt
import pandas as pd
from classes.logger import Logger

class CryptoCoin:
    def __init__(self, name) -> None:
        self.name = name
        self.path = None
        self.interval = None
        self.start = None
        self.end = None

    def get_dataframe(self) -> pd.DataFrame:
        try:
            return pd.read_csv(self.path , index_col=0, parse_dates=True)
        except Exception as ex:
            Logger.log(f"Erro ao abrir {self.path}", ex)
            return None

    def download(self):
        try:
            return vbt.BinanceData.download(self.name, start=self.start, end=self.end, interval=self.interval).get()
        except Exception as ex:
            Logger.log(f'[{self.__class__}] Erro ao fazer download de {self.name}', ex)
            return None
        
    def update(self):
        try:
            self.start = '7 day ago UTC'
            self.end = 'now UTC'
            self.interval = '1h'

            try:
                data = self.get_dataframe()
                self.start = data.index[-1]

                df_new = self.download()

                data = pd.concat([data.iloc[:-1], df_new])
                data.to_csv(self.path)

            except:
                
                data = self.download()

                if len(data) > 1:
                    data.to_csv(self.path)

        except Exception as ex:
            Logger.log(f'[{self.__class__}] Erro ao atualizar dados com o arquivo {self.path}', ex)