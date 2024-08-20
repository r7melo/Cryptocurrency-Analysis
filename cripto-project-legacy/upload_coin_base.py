from BinanceDataDownloader import BinanceDataDownloader
from datetime import datetime
import pandas as pd
import numpy as np

symbols = BinanceDataDownloader.get_symbols()
datetime_now = datetime.now().strftime("%Y%m%d%H%M%S%f")
data_final = pd.DataFrame(columns=['Symbol', 'Trend', 'Last Stand', 'Angle'])

def df0_bigger_dfn(dfs):
    r = []
    for i in range(len(dfs)-2):
        r.append((dfs[i].tail(1) < dfs[i+1].tail(1)).all().all())
    return all(r)

for index, symbol in enumerate(symbols, start=1):

    print(f"[{index}/{len(symbols)}] - {symbol}")

    filename = f'C:/CoinsBase/{symbol}.csv'
    data = BinanceDataDownloader.download(filename, symbol)

