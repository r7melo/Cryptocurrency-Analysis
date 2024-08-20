import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from BinanceDataDownloader import BinanceDataDownloader
import math
import itertools

   
SYMBOL = "BTCUSDT"
filename = f'C:/CoinsBase/{SYMBOL}.csv'
data = BinanceDataDownloader.download(filename, SYMBOL, update=True)

if data is not None:

    # Converter o índice para o fuso horário UTC
    data.index = pd.to_datetime(data.index, utc=True)
    
    # Intevalo para análise
    data = data[-100:]
    
    # INDICADORES
    
    time_graphics_mma = []
    mean_time = ((data['Open'] + data['Close']) / 2)
    mean_720_periods = mean_time.rolling(window=720).mean()
    mean_240_periods = mean_time.rolling(window=240).mean()
    mean_60_periods = mean_time.rolling(window=60).mean()
    mean_geometric = (mean_720_periods*mean_240_periods*mean_60_periods)**(1/3)


    # Desenhando
    # mean_720_periods.plot(color='#a500ff', label='MA (720)')
    # mean_240_periods.plot(color='#c55bff', label='MA (240)')
    # mean_60_periods.plot(color='#dda7f9', label='MA (60)')
    # mean_geometric.plot(color='#d6d9db', label='MA³')
    # mean_time.plot(color='#7fa7ff', label='Center')

   

    # Adicionar legendas e título
    plt.legend()
    plt.title(SYMBOL)
    plt.xlabel('Data')
    plt.ylabel('Preço')
    plt.legend(loc='lower left')
    plt.tight_layout()

    # Exibir o gráfico
    plt.show()

else:
    print(f"Não foi possível fazer a leitura de {SYMBOL}.")