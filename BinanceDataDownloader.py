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
        white_list_criptocoins = []
        try:
            with open("C:/CoinsBase/WHITE_LIST_CRIPTOCOINS.txt", "r") as file:
                white_list_criptocoins = file.read().split('\n')
        except:
            print("Falha ao acessar a lista de símbolos.")

        return white_list_criptocoins

        
