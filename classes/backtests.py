import pandas as pd
import numpy as np
from typing import Tuple

class BackTest:
    
    @staticmethod
    def backtest_setup_by_indicator(df: pd.DataFrame, period: int, indicator_name: str) -> Tuple[pd.DataFrame, dict]:
        """
        Realiza o backtest de um setup de trading com base em um indicador fornecido e avalia o resultado das operações ('Gain' ou 'Loss').
        
        Parâmetros:
        - df (pd.DataFrame): DataFrame contendo as colunas 'High', 'Low', 'Center' e a coluna de sinal indicada por 'indicator_name'.
        - period (int): Número de períodos para calcular os mínimos e máximos futuros.
        - indicator_name (str): Nome da coluna do indicador que contém sinais de 'Buy' (compra) ou 'Sell' (venda).
        
        Retorna:
        - pd.DataFrame: DataFrame com novas colunas 'IndicadorName_Operation' indicando o resultado de cada operação ('Gain' ou 'Loss') .
        - dict: Data com o feedback dos backtests feito nas operações. 
            return - {'NaN', 'Loss', 'Gain', 'Total', 'Gain%', 'Loss%'}
        """
        
        # Identificar sinais de compra e venda
        filter_buy = df[indicator_name] == 'Buy'
        filter_sell = df[indicator_name] == 'Sell'

        # Calcular mínimos e máximos futuros
        min_futures_p = df['Low'].shift(-period).rolling(period).min()
        max_futures_p = df['High'].shift(-period).rolling(period).max()
        
        # Condições para operação de compra
        take_loss_of_operation_buy = df['Low'].shift(1)
        has_stop_loss_of_operation_buy = filter_buy & (min_futures_p <= take_loss_of_operation_buy)
        last_buy_p = df['Low'].shift(-period)
        has_take_profit_of_operation_buy = filter_buy & (last_buy_p > df['Center'])
        
        # Condições para operação de venda
        take_loss_of_operation_sell = df['High'].shift(1)
        has_stop_loss_of_operation_sell = filter_sell & (max_futures_p >= take_loss_of_operation_sell)
        last_sell_p = df['High'].shift(-period)
        has_take_profit_of_operation_sell = filter_sell & (last_sell_p < df['Center'])
        
        # Inicializa a coluna 'Operation' com valor vazio
        df[f'{indicator_name}_Operation'] = 'NaN'

        df.loc[filter_buy, f'{indicator_name}_Operation'] = 'Loss'
        df.loc[filter_sell, f'{indicator_name}_Operation'] = 'Loss'

        df.loc[has_take_profit_of_operation_buy, f'{indicator_name}_Operation'] = 'Gain'
        df.loc[has_take_profit_of_operation_sell, f'{indicator_name}_Operation'] = 'Gain'
        
        # Atualiza a coluna f'{indicator_name}_Operation' com base nas condições
        df.loc[has_stop_loss_of_operation_buy, f'{indicator_name}_Operation'] = 'Loss'
        df.loc[has_stop_loss_of_operation_sell, f'{indicator_name}_Operation'] = 'Loss'
        
        # feedback com a contagem das operacoes realizadas
        data = df[f'{indicator_name}_Operation'].value_counts(dropna=False).to_dict()
        total = df[indicator_name].count()
        feedback = data | {
            "Total": total,
            "Gain%": (data['Gain'] / total) * 100,
            "Loss%": (data['Loss'] / total) * 100
        }
        
        return df, feedback

