import pandas as pd
import numpy as np
from typing import Tuple

class Indicator:

    @staticmethod
    def mean(df: pd.DataFrame, window: int) -> pd.DataFrame:
        """
        Calcula a média móvel simples de uma ou mais colunas de um DataFrame.

        Args:
            df (pd.DataFrame): DataFrame contendo os dados.
            window (int): O tamanho da janela para o cálculo da média móvel.

        Returns:
            pd.DataFrame: DataFrame com a média móvel calculada para cada coluna.
        """
        return df.rolling(window=window).mean()

    @staticmethod
    def exponential_mean(df: pd.DataFrame, span: int) -> pd.DataFrame:
        """
        Calcula a média móvel exponencial de uma ou mais colunas de um DataFrame.

        Args:
            df (pd.DataFrame): DataFrame contendo os dados.
            span (int): O parâmetro 'span' para o cálculo da média móvel exponencial, 
                        que controla o quão suave a média será.

        Returns:
            pd.DataFrame: DataFrame com a média móvel exponencial calculada para cada coluna.
        """
        return df.ewm(span=span, adjust=False).mean()

    @staticmethod
    def compare_displaced(df: pd.DataFrame, column: str, operation: str, periods: int) -> pd.DataFrame:
        """
        Compara uma coluna deslocada do DataFrame utilizando uma operação específica.

        Args:
            df (pd.DataFrame): DataFrame contendo os dados.
            column (str): O nome da coluna a ser comparada.
            operation (str): A operação de agregação a ser aplicada (por exemplo, 'mean', 'sum').
            periods (int): O número de períodos para deslocamento e o tamanho da janela para a operação.

        Returns:
            pd.Series: Série com os resultados da operação aplicada na coluna deslocada.

        Raises:
            ValueError: Se a operação especificada não for válida para a coluna do DataFrame.
        """
        if hasattr(df[column], operation):
            func = getattr(df[column].shift(periods).rolling(window=periods), operation)
            result = func()
            return result.shift(-periods)
        else:
            raise ValueError(f"A operação '{operation}' não é válida para o DataFrame.")
    
    @staticmethod
    def setup_9_1(df: pd.DataFrame) -> pd.DataFrame:
        """
        Aplica o setup 9.1 de Larry Williams para identificar sinais de compra e venda em um DataFrame.

        O setup 9.1 identifica possíveis oportunidades de negociação com base na comparação entre o preço de abertura, fechamento e a média móvel exponencial de 9 períodos (EMA_9):
        - Um sinal de compra ('9_1_Buy') é gerado quando o preço de abertura é menor que a EMA_9 e o preço de fechamento é maior que a EMA_9.
        - Um sinal de venda ('9_1_Sell') é gerado quando o preço de abertura é maior que a EMA_9 e o preço de fechamento é menor que a EMA_9.

        Parâmetros:
        - df (pd.DataFrame): DataFrame contendo as colunas 'Open', 'Close' e 'EMA_9'.

        Retorna:
        - pd.DataFrame: O mesmo DataFrame de entrada com a nova coluna 'Setup_9_1', indicando 'Buy', 'Sell' ou np.nan.
        """
        
        # Inicializa a coluna 'Setup_9_1' com o tipo de dados 'object'
        df['Setup_9_1'] = pd.Series([np.nan] * len(df), dtype='object')
        
        # Condições para identificar os sinais de compra e venda
        buy_condition = (df['Open'] < df['EMA_9']) & (df['Close'] > df['EMA_9'])
        sell_condition = (df['Open'] > df['EMA_9']) & (df['Close'] < df['EMA_9'])
        
        # Atribui os sinais de compra e venda
        df.loc[buy_condition, 'Setup_9_1'] = 'Buy'
        df.loc[sell_condition, 'Setup_9_1'] = 'Sell'

        return df
    
    
    @staticmethod
    def setup_test(df: pd.DataFrame) -> pd.DataFrame:
        """
        Identifica sinais de operação com base na coluna 'Setup_9_1' e avalia o sucesso da operação.
        
        Parâmetros:
        - df_ (pd.DataFrame): DataFrame contendo a coluna 'Setup_9_1' e dados históricos de preço.
        
        Retorna:
        - pd.DataFrame: DataFrame com uma nova coluna 'Operation' indicando se a operação foi 'Gain' ou 'Loss'.
        """

        reason = 3

        # Identificar sinais de compra e venda
        filter_buy = df['Setup_9_1'] == 'Buy'
        filter_sell = df['Setup_9_1'] == 'Sell'

        # Abrindo operação de compra
        min_futures_8p = df['Low'].shift(-8).rolling(8).min()
        take_loss_of_operation_buy = df['Low'].shift(1)
        has_stop_loss_of_operation_buy = filter_buy & (min_futures_8p <= take_loss_of_operation_buy)

        # Abrindo operação de venda
        max_futures_8p = df['High'].shift(-8).rolling(8).max()
        take_loss_of_operation_sell = df['High'].shift(1)
        has_stop_loss_of_operation_sell = filter_sell & (max_futures_8p >= take_loss_of_operation_sell)
        
        df['Operation'] = ''
        df.loc[filter_buy, 'Operation'] = 'Gain'
        df.loc[filter_sell, 'Operation'] = 'Gain'
        df.loc[has_stop_loss_of_operation_buy, 'Operation'] = 'Loss'
        df.loc[has_stop_loss_of_operation_sell, 'Operation'] = 'Loss'

        n_operations = df['Setup_9_1'].notna().sum()
        operations = df['Operation'].value_counts(dropna=False).to_dict()
        percentage_gain = (operations['Gain']/n_operations)*100

        df['Percentage_Gain'] = percentage_gain

        return df
