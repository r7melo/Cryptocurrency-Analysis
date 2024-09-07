import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

symbol = 'EURUSD'
file_path = 'eur_usd_h1_data.csv'
start = None
TIME_EXPIRATION = '1h'


df = pd.read_csv(file_path, index_col=0, parse_dates=True)
if len(df) > 0: 
    start = df.index[-1]

if start is None:
    start = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')
else:
    start = start.strftime('%Y-%m-%d')

new_df = yf.download(symbol, interval=TIME_EXPIRATION, start=start)

# Exibe os dados
print(new_df)

if not df.empty:
    new_df = new_df[~new_df.index.isin(df.iloc[:-1].index)]

# Combine os dados existentes com os novos
data = pd.concat([df.iloc[:-1], new_df])

data.to_csv('eur_usd_h1_data.csv')

print("Dados salvos em 'eur_usd_h1_data.csv'.")
