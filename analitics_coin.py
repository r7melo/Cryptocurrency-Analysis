import matplotlib.pyplot as plt
import pandas as pd
from BinanceDataDownloader import BinanceDataDownloader
import math

SYMBOL = "BTCUSDT"
PORCENTAGEM = 10 #(10% - 100%)
ALAVANCA = 10

filename = f'C:/CoinsBase/{SYMBOL}.csv'
data = BinanceDataDownloader.download(filename, SYMBOL)

if data is not None:

    # Converter o índice para o fuso horário UTC
    data.index = pd.to_datetime(data.index, utc=True)
    
    # INDICADORES
    mean_time = ((data['Open'] + data['Close']) / 2)
    mean_720_periods = mean_time.rolling(window=720).mean()
    mean_240_periods = mean_time.rolling(window=240).mean()
    mean_60_periods = mean_time.rolling(window=60).mean()
    mean_geometric = (mean_720_periods*mean_240_periods*mean_60_periods)**(1/3)
    tops = data['High'].rolling(window=1440).max()
    holes = data['Low'].rolling(window=1440).min()
    tops_mean = tops[-61:-1].median()
    holes_mean = holes[-61:-1].median()
    stop_up = data['High'] * (1 + ((PORCENTAGEM/100)/ALAVANCA))
    stop_down = data['Low'] * (1 - ((PORCENTAGEM/100)/ALAVANCA))

    delta = mean_geometric.iloc[-1] - mean_geometric.iloc[-61] 
    theta_radians = math.atan(delta/60)
    theta_degrees = math.degrees(theta_radians)

    tops_mean = tops[-61:-1].max()
    holes_mean = holes[-61:-1].min()
    stop_sell = (100*(tops_mean - mean_time.iloc[-1]))/mean_time.iloc[-1]
    stop_buy = (100*(holes_mean - mean_time.iloc[-1]))/mean_time.iloc[-1]
    print(stop_buy,stop_sell)

    # Desenhando
    mean_time.plot(color='#09c184', label='Ponto Médio', linewidth=2)
    mean_720_periods.plot(color='#FFFD82', label='MA (720)')
    mean_240_periods.plot(color='#FF9B71', label='MA (240)')
    mean_60_periods.plot(color='#E84855', label='MA (60)')
    mean_geometric.plot(color='#000', label='MA³')
    tops.plot(color='#3F88C5', label='Topo (Max:60)')
    holes.plot(color='#704813', label='Vale (Min:60)')
    plt.axhline(y=tops_mean, color='#3F88C5', linestyle='--', label='Mediana do Topo (60)')
    plt.axhline(y=holes_mean, color='#704813', linestyle='--', label='Mediana do Vale (60)')
    plt.fill_between(data.index, stop_down, stop_up, color='#161917', alpha=0.3, label=f'Variação de {PORCENTAGEM}%')


    # Adicionar legendas e título
    plt.legend()
    plt.title(SYMBOL)
    plt.xlabel('Data')
    plt.ylabel('Preço')

    # Exibir o gráfico
    plt.show()

else:
    print(f"Não foi possível fazer a leitura de {SYMBOL}.")