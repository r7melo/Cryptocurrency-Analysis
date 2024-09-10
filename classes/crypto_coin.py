import vectorbt as vbt
from classes.logger import Logger
from classes.coin_base import CoinBase

class CryptoCoin(CoinBase):
    def __init__(self, name) -> None:
        super().__init__(name)

    def download(self):
        try:
            return vbt.BinanceData.download(self.name, start=self.start, end=self.end, interval=self.interval).get()
        except Exception as ex:
            Logger.log(f'[{self.__class__}] Erro ao fazer download de {self.name}', ex)
            return None
        