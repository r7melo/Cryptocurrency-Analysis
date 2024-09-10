import pandas as pd
from classes.logger import Logger

class CoinBase:
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
        