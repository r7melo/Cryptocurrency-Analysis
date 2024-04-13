import requests

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
binance_symbols = get_binance_symbols()

# Escrever símbolos em um arquivo
write_symbols_to_file(binance_symbols)
