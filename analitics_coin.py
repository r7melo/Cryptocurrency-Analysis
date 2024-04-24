import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from BinanceDataDownloader import BinanceDataDownloader
import math
import itertools


SYMBOL = "BONKUSDT"


filename = f'C:/CoinsBase/{SYMBOL}.csv'
data = BinanceDataDownloader.download(filename, SYMBOL, update=True)

if data is not None:

    # Converter o índice para o fuso horário UTC
    # data.index = pd.to_datetime(data.index, utc=True)
    
    # Intevalo para análise
    data = data[-960:]
    
    # INDICADORES
    mean_time = ((data['Open'] + data['Close']) / 2)
    mean_720_periods = mean_time.rolling(window=720).mean()
    mean_240_periods = mean_time.rolling(window=240).mean()
    mean_60_periods = mean_time.rolling(window=60).mean()
    mean_geometric = (mean_720_periods*mean_240_periods*mean_60_periods)**(1/3)

    #region LOGICA DO PAVIL
    if_buy_condition = lambda m1,m2,m3,m4,m5: (m1 > m2) & (m2 > m3) & (m3 > m4) & (m4 < m5)
    if_sell_condition = lambda m1,m2,m3,m4,m5: (m1 < m2) & (m2 < m3) & (m3 < m4) & (m4 < m5)

    nomes = ['mean_time', 'mean_60_periods', 'mean_240_periods', 'mean_720_periods', 'mean_geometric']
    val = [mean_time, mean_60_periods, mean_240_periods, mean_720_periods, mean_geometric]
    resultado = []

    for comb in itertools.permutations([0,1,2,3,4]):
        
        buy_condition_aux = if_buy_condition(val[comb[0]], val[comb[1]], val[comb[2]], val[comb[3]], val[comb[4]])
        sell_condition_aux = if_sell_condition(val[comb[0]], val[comb[1]], val[comb[2]], val[comb[3]], val[comb[4]])
        buy_aux = (mean_60_periods[buy_condition_aux])
        sell_aux = (mean_60_periods[sell_condition_aux])

        buy_score = (buy_aux[buy_aux.shift(60) < buy_aux]).count()
        sell_score = (sell_aux[sell_aux.shift(60) > sell_aux]).count()

        resultado.append([comb, buy_score, sell_score])

    df = pd.DataFrame(resultado, columns=['Permuta', 'Buy', 'Sell'])
    indice_max_buy = df['Buy'].idxmax()
    indice_max_sell = df['Sell'].idxmax()

    permuta_buy = df.loc[indice_max_buy]['Permuta']
    permuta_sell = df.loc[indice_max_sell]['Permuta']

    buy_condition = if_buy_condition(val[permuta_buy[0]], val[permuta_buy[1]], val[permuta_buy[2]], val[permuta_buy[3]], val[permuta_buy[4]])
    sell_condition = if_sell_condition(val[permuta_sell[0]], val[permuta_sell[1]], val[permuta_sell[2]], val[permuta_sell[3]], val[permuta_sell[4]])
    buy = (mean_time[buy_condition])
    sell = (mean_time[sell_condition])

        


    

    
    
    # buy_delta_x = buy.index.to_series().diff().dt.total_seconds()
    # buy_delta_y = buy.diff()
    # buy_delta_y_numeric = pd.to_numeric(buy_delta_y, errors='coerce')
    # buy_angle = np.degrees(np.arctan2(buy_delta_y_numeric, buy_delta_x))
    # buy_score = buy_angle.mean() * buy.count()

    # sell_delta_x = sell.index.to_series().diff().dt.total_seconds()
    # sell_delta_y = sell.diff()
    # sell_delta_y_numeric = pd.to_numeric(sell_delta_y, errors='coerce')
    # sell_angle = np.degrees(np.arctan2(sell_delta_y_numeric, sell_delta_x))
    # sell_score = sell_angle.mean() * sell.count()


    # dif_ample = mean_time - mean_720_periods
    # max_point_buy = dif_ample.max()
    # max_point_sell = dif_ample.min()


    # print("Score buy: ", buy_score)
    # print("Score sell: ", sell_score)
    # print("Max points buy: ", max_point_buy)
    # print("Max points sell: ", max_point_sell)
    # print(buy_score/max_point_buy, sell_score/max_point_sell)

    # buy_count = buy.rolling(window=60).count()
    # sell_count = sell.rolling(window=60).count()
    # buy_count = buy_count[~buy_count.index.duplicated()]
    # sell_count = sell_count[~sell_count.index.duplicated()]
    # buy_count_aligned, sell_count_aligned = buy_count.align(sell_count, fill_value=0)
    # buy = buy.where(buy_count_aligned < sell_count_aligned, other=None)
    # sell = sell.where(buy_count_aligned > sell_count_aligned, other=None)
    #endregion

    tops_D = data['High'].groupby([data.index.date]).transform('max')
    holes_D = data['Low'].groupby([data.index.date]).transform('min')
    openings_D = data['Open'].groupby([data.index.date]).transform('first')
    closings_D = data['Close'].groupby([data.index.date]).transform('last')

    tops_H = data['High'].groupby([data.index.date, data.index.hour]).transform('max')
    holes_H = data['Low'].groupby([data.index.date, data.index.hour]).transform('min')
    openings_H = data['Open'].groupby([data.index.date, data.index.hour]).transform('first')
    closings_H = data['Close'].groupby([data.index.date, data.index.hour]).transform('last')


  

    # Desenhando
    mean_720_periods.plot(color='#a500ff', label='MA (720)')
    mean_240_periods.plot(color='#c55bff', label='MA (240)')
    mean_60_periods.plot(color='#dda7f9', label='MA (60)')
    mean_geometric.plot(color='#d6d9db', label='MA³')
    mean_time.plot(color='#7fa7ff', label='Center')

    plt.scatter(buy.index, buy, color='#19ff00', marker='.', zorder=2)
    plt.scatter(sell.index, sell, color='#ff0000', marker='.', zorder=2)
    

    plt.fill_between(data.index, holes_D, tops_D, color='#3f7cff', alpha=0.3, label=f'Pavil do dia')
    plt.fill_between(data.index, holes_H, tops_H, color='#7fa7ff', alpha=0.3, label=f'Pavil da hora')
    openings_D.plot(color='#09c184', label='Abertura do dia', linewidth=2)
    closings_D.plot(color='#E84855', label='Fechamento do dia', linewidth=2)
    openings_H.plot(color='#0fffaf', label='Abertura da hora', linewidth=2)
    closings_H.plot(color='#ff727c', label='Fechamento da hora', linewidth=2)

    
    

    # plt.axhline(y=0.0049565, color='red', linestyle='--')
    # plt.axhline(y=0.0050061, color='black', linestyle='--')

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