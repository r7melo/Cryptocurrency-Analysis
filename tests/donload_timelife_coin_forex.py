import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta

def download_data() -> pd.DataFrame:

    symbol = 'EURUSD'
    start_date = datetime(2020, 9, 4)
    end_date = datetime.now()
    timeframe = '15m'


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

            
            print(data.index[-1])
            
            
            current_start = current_end

        mt5.shutdown()

        # Concatenar todos os DataFrames em um único DataFrame
        final_data = pd.concat(all_data)
        final_data = final_data[~final_data.index.duplicated(keep='last')]
        return final_data

    except Exception as ex:
        print(f'Erro ao fazer download de {symbol}: {ex}')
        return None


# Download dos dados
data = download_data()

if data is not None:
    data.to_csv('./data/forex/15m/EURUSD.csv')
    print("Dados baixados e salvos em 'historico_completo_eurusd.csv'")
