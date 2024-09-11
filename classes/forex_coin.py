import vectorbt as vbt
import pandas as pd
from classes.logger import Logger
from datetime import datetime, timedelta
import MetaTrader5 as mt5

class ForexCoin:
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
            # Inicializar o MetaTrader 5
            if not mt5.initialize():
                raise Exception(f"Erro ao inicializar MetaTrader5: {mt5.last_error()}")

            # Definir timeframe do MT5 baseado no intervalo desejado
            timeframe_map = {
                '1m': mt5.TIMEFRAME_M1,
                '5m': mt5.TIMEFRAME_M5,
                '15m': mt5.TIMEFRAME_M15,
                '1h': mt5.TIMEFRAME_H1,
                '1d': mt5.TIMEFRAME_D1,
            }
            mt5_timeframe = timeframe_map.get(self.interval)

            if not mt5_timeframe:
                raise ValueError(f"Intervalo '{self.interval}' não é suportado")

            # Solicitar dados históricos do MetaTrader 5
            rates = mt5.copy_rates_range(self.name, mt5_timeframe, datetime.strptime(self.start, '%Y-%m-%d'), datetime.strptime(self.end, '%Y-%m-%d'))

            # Encerrar a conexão com o MetaTrader 5
            mt5.shutdown()

            # Verificar se os dados foram baixados com sucesso
            if rates is None or len(rates) == 0:
                raise Exception(f"Nenhum dado encontrado para {self.name} no intervalo especificado.")

            # Converter para DataFrame do pandas
            data = pd.DataFrame(rates)
            data['time'] = pd.to_datetime(data['time'], unit='s')  # Converter o timestamp para datetime
            data.set_index('time', inplace=True)

            # Mapear e renomear colunas
            data = data.rename(columns={
                'open': 'Open',
                'high': 'High',
                'low': 'Low',
                'close': 'Close',
                'tick_volume': 'Volume'
            })

            # Adicionar colunas adicionais com NaN ou valores padrão
            data['Open time'] = data.index
            data['Close time'] = pd.NA  # Defina como o mesmo valor se não houver dados de fechamento disponíveis
            data['Quote volume'] = pd.NA
            data['Number of trades'] = pd.NA
            data['Taker base volume'] = pd.NA
            data['Taker quote volume'] = pd.NA

            # Reordenar as colunas
            data = data[['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote volume', 'Number of trades', 'Taker base volume', 'Taker quote volume']]
            data.set_index('Open time', inplace=True)

            return data

        except Exception as ex:
            Logger.log(f'[{self.__class__.__name__}] Erro ao fazer download de {self.name}', ex)
            return None

    def update(self):
        try:
            # Atualizar o intervalo de tempo
            self.start = (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d')
            self.end = datetime.now().strftime('%Y-%m-%d')
            self.interval = '15m'

            # Manter o nome original
            original_name = self.name

            try:
                # Carregar dados existentes
                data = self.get_dataframe()
                self.start = data.index[-1].strftime('%Y-%m-%d')  # Atualizar o início para a última data

                # Fazer o download dos dados novos
                df_new = self.download()

                # Concatenar e salvar
                if df_new is not None and not df_new.empty:
                    data = pd.concat([data.iloc[:-1], df_new])
                    data.to_csv(self.path)

            except Exception as inner_ex:
                Logger.log(f'[{self.__class__.__name__}] Erro ao carregar ou combinar dados para {self.name}', inner_ex)

                # Fazer o download diretamente se houver erro
                data = self.download()

                if data is not None and len(data) > 1:
                    data.to_csv(self.path)

            finally:
                # Restaurar o nome original
                self.name = original_name

        except Exception as ex:
            Logger.log(f'[{self.__class__.__name__}] Erro ao atualizar dados com o arquivo {self.path}', ex)
