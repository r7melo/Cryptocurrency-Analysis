import multiprocessing
import requests
import time
import csv
from datetime import datetime, timedelta

LOGINFO = True
URL_COINBASE = 'C:/CoinsBase/'
URL_BINANCE_INFO = 'https://api.binance.com/api/v3/exchangeInfo'
URL_BINANCE_KLINES = 'https://api.binance.com/api/v1/klines'
DELAY = 60

def logInfo(message):
    if LOGINFO: print(message)

class BinanceDataDownloader:

    @staticmethod
    def download(filename, symbol="BTCUSDT", interval='1m', update=True):
        data = None

        try:
            data = pd.read_csv(filename, index_col=0, parse_dates=True)
            logInfo("Dados carregados do arquivo local.")

            if not update: return data

            if len(data) > 100:
                start_time = data.index[-1]
                
                params = {
                    'symbol': symbol,
                    'interval': interval,
                    'limit': 1000,
                    'startTime': start_time
                }

                response = requests.get(URL_BINANCE_KLINES, params=params)
                if response.status_code == 200:
                    candlestick_data = response.json()
                    if candlestick_data:
                        with open(URL_COINBASE+symbol+'.csv', 'w', newline='') as f:
                            writer = csv.writer(f)
                            for candlestick in candlestick_data:
                                writer.writerow(candlestick)

                    print(symbol)
                    logInfo("Dados atualizados e salvos no arquivo local.")
                
                else:
                    print('Erro ao obter dados da API da Binance: {}'.format(response.status_code))
                    return None

            else:
                print("Arquivo não contem mais de 100 registros.")

        except:
            logInfo("Arquivo local não encontrado.")

            current_time = datetime.now()
            five_days_ago = current_time - timedelta(days=5)
            start_time = int(five_days_ago.timestamp() * 1000)

            params = {
                'symbol': symbol,
                'interval': interval,
                'limit': 1000,
                'startTime': start_time
            }

            response = requests.get(URL_BINANCE_KLINES, params=params)
            if response.status_code == 200:
                candlestick_data = response.json()
                if candlestick_data:
                    with open(URL_COINBASE+symbol+'.csv', 'w', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow(['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume', 'Number of trades', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore'])
                        for candlestick in candlestick_data:
                            writer.writerow(candlestick)

            logInfo("Arquivo local gerado.")

        return data

 
    @staticmethod
    def get_symbols(filter="USDT"):
       
        response = requests.get(URL_BINANCE_INFO)
        blocked_list = []

        try:
            with open(URL_COINBASE+"BLOCKED_LIST.txt", "r") as file:
                blocked_list = file.read().split('\n')
        except:
            print("Falha ao acessar a lista de símbolos bloqueados.")

        if response.status_code == 200:
            exchange_info = response.json()
            symbols = [symbol['symbol'] for symbol in exchange_info['symbols'] if filter in symbol['symbol'] and symbol['symbol'] not in blocked_list]
            return symbols
        
        else:
            print("Falha ao obter a lista de símbolos da Binance.")
            return []
        

# Função para processar uma moeda
def valide_coin(symbol):
    filename = '{}/{}.csv'.format(URL_BINANCE_INFO, symbol)
    BinanceDataDownloader.download(filename, symbol, update=True)

# Função para processar uma lista de moedas
def processar_moedas(symbols):
    for symbol in symbols:
        filename = URL_COINBASE+symbol+'.csv'
        BinanceDataDownloader.download(filename, symbol, update=True)

if __name__ == "__main__":

    while True:
        # Obtendo a lista de símbolos
        symbols = BinanceDataDownloader.get_symbols()
        processed = 0

        # Configurando o multiprocessing
        num_processes = multiprocessing.cpu_count()  # Usando o número de núcleos da CPU
        chunk_size = len(symbols) // num_processes  # Dividindo a lista de símbolos em partes iguais para cada processo

        # Dividindo a lista de símbolos em partes iguais para cada processo
        symbol_chunks = [symbols[i:i+chunk_size] for i in range(0, len(symbols), chunk_size)]

        # Criando e iniciando os processos
        with multiprocessing.Pool(processes=num_processes) as pool:
            pool.map(processar_moedas, symbol_chunks)

        time.sleep(DELAY)
