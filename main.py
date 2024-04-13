from BinanceDataDownloader import BinanceDataDownloader
from datetime import datetime
import pandas as pd
import math
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

    if data is not None:
        mean_time = ((data['Open'] + data['Close']) / 2)
        mean_1600_periods = mean_time.rolling(window=720).mean()
        mean_800_periods = mean_time.rolling(window=240).mean()
        mean_400_periods = mean_time.rolling(window=60).mean()
        mean_geometric = (mean_1600_periods*mean_800_periods*mean_400_periods)**(1/3)
       
        delta = mean_geometric.iloc[-1] - mean_geometric.iloc[-61] 
        theta_radians = math.atan(delta/60)
        theta_degrees = math.degrees(theta_radians)
        
        tops = data['High'].rolling(window=1440).max()
        holes = data['Low'].rolling(window=1440).min()
        tops_mean = tops[-61:-1].max()
        holes_mean = holes[-61:-1].min()
        stop_sell = (100*(tops_mean - mean_time.iloc[-1]))/mean_time.iloc[-1]
        stop_buy = (100*(holes_mean - mean_time.iloc[-1]))/mean_time.iloc[-1]
                
        if df0_bigger_dfn([mean_1600_periods, mean_geometric, mean_800_periods, mean_400_periods]):
            return {'Symbol': symbol, 'Trend': 'SELL', 'Last Stand': mean_time.iloc[-1], 'Angle': theta_degrees, 'Stop Sell': stop_sell, 'Stop Buy': stop_buy}
        elif df0_bigger_dfn([mean_400_periods, mean_800_periods, mean_geometric, mean_1600_periods]):
            return ({'Symbol': symbol, 'Trend': 'BUY', 'Last Stand': mean_time.iloc[-1], 'Angle': theta_degrees, 'Stop Sell': stop_sell, 'Stop Buy': stop_buy})
        else:
            return ({'Symbol': symbol, 'Trend': '--', 'Last Stand': mean_time.iloc[-1], 'Angle': theta_degrees, 'Stop Sell': stop_sell, 'Stop Buy': stop_buy})
    

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
    if len(data_final) > 0:
        data_final = data_final.sort_values(by='Angle', ascending=False)

    # Salvando os resultados
    datetime_now = datetime.now().strftime("%Y%m%d%H%M%S%f")
    data_final.to_csv(f'./trend_base/trend_list_{datetime_now}.csv', index=False)
