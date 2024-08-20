from BinanceDataDownloader import BinanceDataDownloader
from datetime import datetime
import pandas as pd
import itertools
import numpy as np
import multiprocessing

def df0_bigger_dfn(dfs):
    r = []
    for i in range(len(dfs)-1):
        r.append((dfs[i].tail(1) > dfs[i+1].tail(1)).all().all())
    return all(r)

# Função para processar uma moeda
def valide_coin(symbol):
    filename = f'C:/CoinsBase/{symbol}.csv'
    data = BinanceDataDownloader.download(filename, symbol, update=True)

    # if data is not None:
    #     # Intevalo para análise
    #     data = data[-960:]
        
    #     # INDICADORES
    #     mean_time = ((data['Open'] + data['Close']) / 2)
    #     mean_720_periods = mean_time.rolling(window=720).mean()
    #     mean_240_periods = mean_time.rolling(window=240).mean()
    #     mean_60_periods = mean_time.rolling(window=60).mean()
    #     mean_geometric = (mean_720_periods*mean_240_periods*mean_60_periods)**(1/3)

    #     #region LOGICA DO PAVIL
    #     if_buy_condition = lambda m1,m2,m3,m4,m5: (m1 > m2) & (m2 > m3) & (m3 > m4) & (m4 < m5)
    #     if_sell_condition = lambda m1,m2,m3,m4,m5: (m1 < m2) & (m2 < m3) & (m3 < m4) & (m4 < m5)

    #     val = [mean_time, mean_60_periods, mean_240_periods, mean_720_periods, mean_geometric]
    #     resultado = []

    #     for comb in itertools.permutations([0,1,2,3,4]):
            
    #         buy_condition_aux = if_buy_condition(val[comb[0]], val[comb[1]], val[comb[2]], val[comb[3]], val[comb[4]])
    #         sell_condition_aux = if_sell_condition(val[comb[0]], val[comb[1]], val[comb[2]], val[comb[3]], val[comb[4]])
    #         buy_aux = (mean_60_periods[buy_condition_aux])
    #         sell_aux = (mean_60_periods[sell_condition_aux])

    #         buy_score = (buy_aux[buy_aux.shift(60) < buy_aux]).count()
    #         sell_score = (sell_aux[sell_aux.shift(60) > sell_aux]).count()

    #         resultado.append([comb, buy_score, sell_score])

    #     df = pd.DataFrame(resultado, columns=['Permuta', 'Buy', 'Sell'])
    #     indice_max_buy = df['Buy'].idxmax()
    #     indice_max_sell = df['Sell'].idxmax()

    #     permuta_buy = df.loc[indice_max_buy]['Permuta']
    #     permuta_sell = df.loc[indice_max_sell]['Permuta']

    #     buy_condition = if_buy_condition(val[permuta_buy[0]], val[permuta_buy[1]], val[permuta_buy[2]], val[permuta_buy[3]], val[permuta_buy[4]])
    #     sell_condition = if_sell_condition(val[permuta_sell[0]], val[permuta_sell[1]], val[permuta_sell[2]], val[permuta_sell[3]], val[permuta_sell[4]])
    #     buy = (mean_time[buy_condition])
    #     sell = (mean_time[sell_condition])

            
    #     buy_delta_x = buy.index.to_series().diff().dt.total_seconds()
    #     buy_delta_y = buy.diff()
    #     buy_delta_y_numeric = pd.to_numeric(buy_delta_y, errors='coerce')
    #     buy_angle = np.degrees(np.arctan2(buy_delta_y_numeric, buy_delta_x))
    #     buy_angle_mean = buy_angle.mean()
    #     buy_count = buy.count()
    #     buy_score = buy_angle_mean * buy_count

    #     sell_delta_x = sell.index.to_series().diff().dt.total_seconds()
    #     sell_delta_y = sell.diff()
    #     sell_delta_y_numeric = pd.to_numeric(sell_delta_y, errors='coerce')
    #     sell_angle = np.degrees(np.arctan2(sell_delta_y_numeric, sell_delta_x))
    #     sell_angle_mean = sell_angle.mean()
    #     sell_count = sell.count()
    #     sell_score = sell_angle_mean * sell_count


    #     dif_ample = mean_time - mean_720_periods
    #     max_point_buy = dif_ample.max()
    #     max_point_sell = dif_ample.min()
        
    #     probability_buy = abs(buy_score/max_point_buy)
    #     probability_sell = abs(sell_score/max_point_sell)

    #     if probability_buy > probability_sell: return { 'Symbol': symbol, 'Score': probability_buy}
    #     else: return  { 'Symbol': symbol, 'Score': probability_sell}


# Função para processar uma lista de moedas
def processar_moedas(symbols):
    results = []
    for symbol in symbols:
        result = valide_coin(symbol)
        if result:
            results.append(result)

    return results

if __name__ == "__main__":
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
        results = pool.map(processar_moedas, symbol_chunks)

    # Concatenando os resultados de todos os processos
    final_results = [result for sublist in results for result in sublist]

    # Convertendo os resultados em um DataFrame e ordenando
    data_final = pd.DataFrame(final_results)
    data_final = data_final.sort_values(by='Score', ascending=False)

    # Salvando os resultados
    datetime_now = datetime.now().strftime("%Y%m%d%H%M%S%f")
    data_final.to_csv(f'./trend_base/trend_list_{datetime_now}.csv', index=False)
