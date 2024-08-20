import requests
import pandas as pd
import vectorbt as vbt

COIN_BASE_PATH = 'C:/CoinsBase/1h/{}.csv'

def get_usdt_futures_pairs():

    url = "https://fapi.binance.com/fapi/v1/exchangeInfo" 
    response = requests.get(url)
    data = response.json()

    usdt_pairs = []
    for symbol_info in data['symbols']:
        if symbol_info['quoteAsset'] == 'USDT': 
            usdt_pairs.append(symbol_info['symbol'])

    with open("C:/CoinsBase/WHITE_LIST_CRIPTOCOINS.txt", "w") as file:
        file.writelines('\n'.join(usdt_pairs))

    return usdt_pairs


def download(symbol, start):
    
    try:
        binance_data = vbt.BinanceData.download(
            symbol,
            start=start,
            end='now UTC',
            interval='1h'
        )

        return binance_data.get()
    
    except:
        return []

    
for symbol in get_usdt_futures_pairs():
    print('---')

    start = '7 day ago UTC'
    path = COIN_BASE_PATH.format(symbol)
    
    try:
        data = pd.read_csv(path, index_col=0, parse_dates=True)
        print(symbol+" - Dados carregados do arquivo local.")
        
        start = data.index[-1]
        data = pd.concat([data.iloc[:-1], download(symbol, start)])
        data.to_csv(path)
        print(symbol+" - Arquivo local atualizado.")

    except:
        
        data = download(symbol, start)

        if len(data) > 1:
            data.to_csv(path)
            print(symbol+" - Arquivo local gerado.")

        
