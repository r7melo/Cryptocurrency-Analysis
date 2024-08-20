import requests
from BinanceDataDownloader import BinanceDataDownloader

def get_binance_symbols():
    url = 'https://api.binance.com/api/v3/exchangeInfo'
    response = requests.get(url)
    if response.status_code == 200:
        exchange_info = response.json()
        symbols = [symbol['symbol'] for symbol in exchange_info['symbols']]
        return symbols
    else:
        print("Falha ao obter a lista de símbolos da Binance.")
        return []

def write_symbols_to_file(symbols, filename='./../coins/binance_symbols.txt'):
    with open(filename, 'w') as file:
        for symbol in symbols:
            file.write(symbol + '\n')

# Obter lista de símbolos da Binance
binance_symbols = [symbol for symbol in get_binance_symbols() if 'USDT' in symbol] 


for index, symbol in enumerate(binance_symbols, start=1):
    print(f"[{index}/{len(binance_symbols)}] - {symbol}")
    downloader = BinanceDataDownloader(symbol)
    filename = f'C:/CoinsBase/{symbol}.csv'
    dados = downloader.load_data(filename)
    downloader.update_data(dados, filename)