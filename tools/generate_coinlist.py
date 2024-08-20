import requests

def get_usdt_pairs():
    url = "https://api.binance.com/api/v3/exchangeInfo"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        symbols = data.get('symbols', [])
        
        # Filtrar pares que envolvem USDT
        usdt_pairs = [symbol_info['symbol'] for symbol_info in symbols if symbol_info['quoteAsset'] == 'USDT']
        
        return usdt_pairs
    else:
        raise Exception("Failed to fetch data from Binance API")

def save_pairs_to_file(pairs, filename):
    with open(filename, 'w') as file:
        for pair in pairs:
            file.write(f"{pair}\n")

if __name__ == "__main__":
    try:
        usdt_pairs = get_usdt_pairs()
        filename = "WHITE_LIST_CRIPTOCOINS.txt"
        save_pairs_to_file(usdt_pairs, filename)
        print(f"Pares de moedas envolvendo USDT foram salvos em '{filename}'.")
    except Exception as e:
        print(f"Erro: {e}")
