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
            return pd.read_csv(self.path , index_col=0, parse_dates=False)
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
            # Define o período e intervalo para o download de dados
            self.start = pd.Timestamp('2020-01-01')
            self.end = pd.Timestamp.now()
            self.interval = '1h'

            try:
                # Carrega o DataFrame existente
                data = self.get_dataframe()

                # Atualiza o valor de self.start com a última data disponível
                if data is not None and not data.empty:
                    self.start = data.index[-1]

                # Faz o download dos novos dados
                df_new = self.download()

                if df_new is not None and not df_new.empty:
                    # Concatena os novos dados com os existentes e remove duplicatas
                    data = pd.concat([data[:-1], df_new])
                    data = data[~data.index.duplicated(keep='last')]
                    data.to_csv(self.path)

            except Exception as ex:
                # Se ocorrer algum erro, realiza o download em blocos
                Logger.log(f"Erro ao atualizar com o DataFrame existente: {ex}")

                # Divide o período em blocos de 1000 horas
                date_range = pd.date_range(start=self.start, end=self.end, freq='1000h')

                data = pd.DataFrame()

                for i in range(len(date_range) - 1):
                    self.start = date_range[i]
                    self.end = date_range[i + 1]

                    # Faz o download de um bloco de dados
                    df_chunk = self.download()

                    if df_chunk is not None and not df_chunk.empty:
                        data = pd.concat([data, df_chunk])

                # Salva os dados somente se houver registros
                if len(data) > 1:
                    data = data[~data.index.duplicated(keep='last')]
                    data.to_csv(self.path)

        except Exception as ex:
            Logger.log(f'[{self.__class__}] Erro ao atualizar dados com o arquivo {self.path}', ex)
