import ccxt
import pandas as pd
from datetime import datetime

def download_crypto_data(symbol: str, timeframe: str, start_date: str) -> pd.DataFrame:
    # Inicializar a conexão com a Binance
    binance = ccxt.binance()

    # Converter a data de início para timestamp
    since = binance.parse8601(f'{start_date}T00:00:00Z')

    # Mapear o timeframe para o formato aceito pela Binance
    timeframe_map = {
        '1m': '1m',
        '5m': '5m',
        '15m': '15m',
        '1h': '1h',
        '1d': '1d',
    }
    binance_timeframe = timeframe_map.get(timeframe)

    if not binance_timeframe:
        raise ValueError(f"Intervalo de tempo '{timeframe}' não é suportado")

    all_data = []
    while since < binance.milliseconds():
        # Baixar dados históricos
        ohlcv = binance.fetch_ohlcv(symbol, binance_timeframe, since)

        if len(ohlcv) == 0:
            break

        # Converter os dados em DataFrame
        data = pd.DataFrame(ohlcv, columns=['timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
        data['Open time'] = pd.to_datetime(data['timestamp'], unit='ms')
        data['Close time'] = pd.NA
        data['Quote volume'] = pd.NA
        data['Number of trades'] = pd.NA
        data['Taker base volume'] = pd.NA
        data['Taker quote volume'] = pd.NA
        data = data[['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote volume', 'Number of trades', 'Taker base volume', 'Taker quote volume']]
        data.set_index('Open time', inplace=True)
        all_data.append(data)
        print(data.index[-1])

        # Atualizar o timestamp para continuar o download de dados
        since = ohlcv[-1][0] + 1

    # Concatenar todos os DataFrames em um único DataFrame
    final_data = pd.concat(all_data)
    final_data = final_data[~final_data.index.duplicated(keep='last')]
    return final_data


symbol = 'OMG'
# Exemplo de uso para baixar dados de BTCUSDT
data = download_crypto_data(f'{symbol}/USDT', '15m', '2022-09-04')

# Salvar os dados em um arquivo CSV 
if data is not None:
    data.to_csv(f'./data/crypto/15m/{symbol}USDT.csv')
    print(f"Dados baixados e salvos em './data/crypto/15m/{symbol}USDT.csv'")
