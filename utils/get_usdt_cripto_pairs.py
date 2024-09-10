import requests

def get_usdt_cripto_pairs() -> list[str]:

    url = "https://fapi.binance.com/fapi/v1/exchangeInfo" 
    response = requests.get(url)
    data = response.json()

    usdt_pairs = []
    for symbol_info in data['symbols']:
        if symbol_info['quoteAsset'] == 'USDT': 
            usdt_pairs.append(symbol_info['symbol'])

    return usdt_pairs