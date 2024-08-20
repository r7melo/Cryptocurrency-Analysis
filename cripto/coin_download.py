import requests
import time
import csv
from datetime import datetime, timedelta
from pathlib import Path


PATH_LOGINFO = "./"
PATH_COINBASE = Path('./CoinsBase')
PATH_COIN_LIST = Path('WhiteListCriptoCoin.txt')
URL_BINANCE_KLINES = 'https://api.binance.com/api/v1/klines'
DELAY = 60

class LogInfo:

    @staticmethod
    def write(menssage):
        datetime_now = datetime.now()
        day_str = datetime_now.strftime("%Y%m%d")
        datetime_str = datetime_now.strftime("%d-%m-%Y %H:%M:%S.%f")

        with open("{}log-{}".format(PATH_LOGINFO,day_str), "a") as fileLog:
            fileLog.write("[{}] {}\n".format(datetime_str, menssage))

class BinanceRequest:

    @staticmethod
    def request(url, symbol, interval, limit, start_time):
        params = { 'symbol': symbol, 'interval': interval, 'limit': limit, 'startTime': start_time }

        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            LogInfo.write("Erro ao obter dados da API da Binance: {}".format(response.status_code))

        return None

class BinanceDataDownloader:

    @staticmethod
    def get_last_date(path_symbol):
        if path_symbol.exists():
            with path_symbol.open(mode='r', newline='') as file_csv:
                reader = csv.reader(file_csv)
                linhas = list(reader)
                datetime_str = linhas[-1][0]
                data_datetime = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
                data_datetime += timedelta(minutes=1)
                return int(data_datetime.timestamp() * 1000)
        return None

    @staticmethod
    def download(path_symbol):

        start_time = BinanceDataDownloader.get_last_date(path_symbol)

        if not path_symbol.exists():
            with path_symbol.open(mode='w') as file_list:
                file_list.write("Open time,Open,High,Low,Close,Volume,Close time,Quote asset volume,Number of trades,Taker buy base asset volume,Taker buy quote asset volume,Ignore\n")
            start_time = int((datetime.now() - timedelta(days=5)).timestamp() * 1000)

        data = BinanceRequest.request(URL_BINANCE_KLINES, path_symbol.stem, '1m', 1000, start_time)

        if data:
            with path_symbol.open(mode='a') as  file_list:
                for line in data:

                    datetime_int = datetime.fromtimestamp(line[0] / 1000)
                    line[0] = datetime_int.strftime("%Y-%m-%d %H:%M:%S")

                    file_list.write(','.join([str(item) for item in line])+'\n')

            
        
        
 
    @staticmethod
    def get_symbols_by_file_list(path_file_list):

        if path_file_list.exists():
            with path_file_list.open() as  file_list:
                return file_list.readlines()
        else:
            LogInfo.write("Não foi possível carregar a lista de criptomoedas.")
        

if __name__ == "__main__":

    coins_list = BinanceDataDownloader.get_symbols_by_file_list(PATH_COIN_LIST)

    while True:
        
        for symbol in coins_list:
            path_symbol = PATH_COINBASE.joinpath("{}.csv".format(symbol.strip()))
            BinanceDataDownloader.download(path_symbol)
            
        time.sleep(DELAY)

