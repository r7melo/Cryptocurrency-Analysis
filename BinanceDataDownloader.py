import vectorbt as vbt
import pandas as pd
import requests

LOGINFO = False

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

            if len(data) > 2000:
                last_line = data.index[-1]
                update_data = vbt.BinanceData.download(
                    symbol,
                    start=last_line,
                    end='now UTC',
                    interval=interval
                )
                data = pd.concat([data, update_data.get()])
                data.to_csv(filename)

                logInfo("Dados atualizados e salvos no arquivo local.")

            else:
                print("Arquivo não contem mais de 2000 registros.")

        except:
            logInfo("Arquivo local não encontrado.")

            binance_data = vbt.BinanceData.download(
                symbol,
                start='7 day ago UTC',
                end='now UTC',
                interval=interval
            )
            data = binance_data.get()

            data.to_csv(filename)

            logInfo("Arquivo local gerado.")

        return data

 
    @staticmethod
    def get_symbols(filter="USDT"):
       
        url = 'https://api.binance.com/api/v3/exchangeInfo'
        response = requests.get(url)
        blocked_list = []

        try:
            with open("C:/CoinsBase/BLOCKED_LIST.txt", "r") as file:
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
        
