import matplotlib.pyplot as plt
import pandas as pd
from BinanceDataDownloader import BinanceDataDownloader
import math

SYMBOL = "BTCUSDT"


filename = f'C:/CoinsBase/{SYMBOL}.csv'
data = BinanceDataDownloader.download(filename, SYMBOL)

if data is not None:

    # Converter o índice para o fuso horário UTC
    data.index = pd.to_datetime(data.index, utc=True)
    
    # Intevalo para análise
    data = data['2024-04-01':]
    
    # INDICADORES
    mean_time = ((data['Open'] + data['Close']) / 2)
    mean_720_periods = mean_time.rolling(window=720).mean()
    mean_240_periods = mean_time.rolling(window=240).mean()
    mean_60_periods = mean_time.rolling(window=60).mean()
    mean_geometric = (mean_720_periods*mean_240_periods*mean_60_periods)**(1/3)

    tops_D = data['High'].groupby(data.index.date).transform('max')
    holes_D = data['Low'].groupby(data.index.date).transform('min')
    openings_D = data['Open'].groupby(data.index.date).transform('first')
    closings_D = data['Close'].groupby(data.index.date).transform('last')

    tops_H = data['High'].groupby([data.index.date, data.index.hour]).transform('max')
    holes_H = data['Low'].groupby([data.index.date, data.index.hour]).transform('min')
    openings_H = data['Open'].groupby([data.index.date, data.index.hour]).transform('first')
    closings_H = data['Close'].groupby([data.index.date, data.index.hour]).transform('last')

    # Desenhando
    mean_720_periods.plot(color='#a500ff', label='MA (720)')
    mean_240_periods.plot(color='#c55bff', label='MA (240)')
    mean_60_periods.plot(color='#dda7f9', label='MA (60)')
    mean_geometric.plot(color='#000', label='MA³')

    plt.fill_between(data.index, holes_D, tops_D, color='#3f7cff', alpha=0.3, label=f'Pavil do dia')
    openings_D.plot(color='#09c184', label='Abertura do dia', linewidth=2)
    closings_D.plot(color='#E84855', label='Fechamento do dia', linewidth=2)

    plt.fill_between(data.index, holes_H, tops_H, color='#7fa7ff', alpha=0.3, label=f'Pavil da hora')
    openings_H.plot(color='#0fffaf', label='Abertura da hora', linewidth=2)
    closings_H.plot(color='#ff727c', label='Fechamento da hora', linewidth=2)


    

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