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

        symbol = self.name
        start_date = self.start
        end_date = self.end
        timeframe = self.interval

        try:
            if not mt5.initialize():
                raise Exception(f"Erro ao inicializar MetaTrader5: {mt5.last_error()}")

            timeframe_map = {
                '1m': mt5.TIMEFRAME_M1,
                '5m': mt5.TIMEFRAME_M5,
                '15m': mt5.TIMEFRAME_M15,
                '1h': mt5.TIMEFRAME_H1,
                '1d': mt5.TIMEFRAME_D1,
            }
            mt5_timeframe = timeframe_map.get(timeframe)
            
            if not mt5_timeframe:
                raise ValueError(f"Intervalo '{timeframe}' não é suportado")

            all_data = []
            current_start = start_date

            while current_start < end_date:
                current_end = min(current_start + timedelta(days=60), end_date)
                rates = mt5.copy_rates_range(symbol, mt5_timeframe, current_start, current_end)

                if rates is None or len(rates) == 0:
                    raise Exception(f"Nenhum dado encontrado para {symbol} no intervalo {current_start} a {current_end}")

                data = pd.DataFrame(rates)
                data['time'] = pd.to_datetime(data['time'], unit='s')
                data.set_index('time', inplace=True)
                data = data.rename(columns={
                    'open': 'Open',
                    'high': 'High',
                    'low': 'Low',
                    'close': 'Close',
                    'tick_volume': 'Volume'
                })
                data['Open time'] = data.index
                data['Close time'] = pd.NA
                data['Quote volume'] = pd.NA
                data['Number of trades'] = pd.NA
                data['Taker base volume'] = pd.NA
                data['Taker quote volume'] = pd.NA
                data = data[['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote volume', 'Number of trades', 'Taker base volume', 'Taker quote volume']]
                data.set_index('Open time', inplace=True)
                all_data.append(data)
                
                current_start = current_end

            mt5.shutdown()

            # Concatenar todos os DataFrames em um único DataFrame
            final_data = pd.concat(all_data)
            final_data = final_data[~final_data.index.duplicated(keep='last')]
            return final_data

        except Exception as ex:
            Logger.log(f'[{self.__class__.__name__}] Erro ao fazer download de {self.name}', ex)
            return None

    def update(self):
        try:
            # Atualizar o intervalo de tempo
            self.start = datetime(2020, 9, 4)
            self.end = datetime.now()
            self.interval = '15m'

            try:
                # Carregar dados existentes
                data = self.get_dataframe()
                self.start = data.index[-1].strftime('%Y-%m-%d')  # Atualizar o início para a última data

                # Fazer o download dos dados novos
                df_new = self.download()

                # Concatenar e salvar
                if df_new is not None and not df_new.empty:
                    data = pd.concat([data.iloc[:-1], df_new])
                    data = data[~data.index.duplicated(keep='last')]
                    data.to_csv(self.path)

            except Exception as inner_ex:
                Logger.log(f'[{self.__class__.__name__}] Erro ao carregar ou combinar dados para {self.name}', inner_ex)

                # Fazer o download diretamente se houver erro
                data = self.download()

                if data is not None and len(data) > 1:
                    data.to_csv(self.path)


        except Exception as ex:
            Logger.log(f'[{self.__class__.__name__}] Erro ao atualizar dados com o arquivo {self.path}', ex)
