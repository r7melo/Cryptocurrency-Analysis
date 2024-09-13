import pandas as pd
import numpy as np
from typing import Tuple
from scipy.stats import linregress
from utils.center_of_force import center_of_force


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
    def cut_candle(df: pd.DataFrame, column_name:str) -> pd.DataFrame:
        """
        Aplica a coluna indicada entre a abertura e fechamento do candle.

        O setup 9.1 identifica possíveis oportunidades de negociação com base na comparação entre o preço de abertura, fechamento e a média móvel exponencial de 9 períodos (EMA_9):
        - Um sinal de compra ('ColumnName_Cut_Candle') é gerado quando o preço de abertura é menor que a ColumnName e o preço de fechamento é maior que a ColumnName.
        - Um sinal de venda ('ColumnName_Cut_Candle') é gerado quando o preço de abertura é maior que a ColumnName e o preço de fechamento é menor que a ColumnName.

        Parâmetros:
        - df (pd.DataFrame): DataFrame contendo as colunas 'Open', 'Close' e 'ColumnName'.

        Retorna:
        - pd.DataFrame: O mesmo DataFrame de entrada com a nova coluna 'ColumnName_Cut_Candle', indicando 'Buy', 'Sell' ou np.nan.
        """
        
        # Inicializa a coluna 'Setup_9_1' com o tipo de dados 'object'
        df[f'{column_name}_Cut_Candle'] = pd.Series([np.nan] * len(df), dtype='object')
        
        # Condições para identificar os sinais de compra e venda
        buy_condition = (df['Open'] < df[column_name]) & (df['Close'] > df[column_name])
        sell_condition = (df['Open'] > df[column_name]) & (df['Close'] < df[column_name])
        
        # Atribui os sinais de compra e venda
        df.loc[buy_condition, f'{column_name}_Cut_Candle'] = 'Buy'
        df.loc[sell_condition, f'{column_name}_Cut_Candle'] = 'Sell'

        return df
    
    @staticmethod
    def approximate_values(df: pd.DataFrame, columns: list, tolerance=0) -> pd.Series:
        """
        Verifica se os valores em cada linha de um DataFrame estão próximos dentro de uma tolerância especificada.

        Parâmetros:
        - df (pd.DataFrame): DataFrame contendo as colunas a serem comparadas.
        - columns (list): Lista com os nomes das colunas a serem comparadas.
        - tolerance (float): A diferença máxima permitida para considerar os valores como próximos (padrão: 0).

        Retorna:
        - pd.Series: Série booleana indicando se os valores em cada linha estão próximos.
        """
        # Verifica se há pelo menos duas colunas para comparar
        if len(columns) < 2:
            raise ValueError("É necessário ao menos duas colunas para realizar a comparação.")

        # Inicializa uma série booleana com True para todas as linhas
        result = pd.Series([True] * len(df), index=df.index)

        # Loop para comparar as colunas especificadas
        for i in range(len(columns) - 1):
            # Calcula a diferença absoluta entre colunas consecutivas
            comparison = abs(df[columns[i]] - df[columns[i + 1]]) <= tolerance
            # Atualiza o resultado com uma operação lógica "E" para manter as verificações anteriores
            result = result & comparison

        return result


    @staticmethod
    def approximate_angles_with_tolerance(df: pd.DataFrame, columns: list, tolerance_percent: float = 100) -> pd.Series:
        """
        Verifica se as diferenças de ângulo entre pontos consecutivos em colunas de um DataFrame 
        estão dentro de uma tolerância baseada em uma porcentagem da média das diferenças de ângulo.

        Parâmetros:
        - df (pd.DataFrame): DataFrame contendo as colunas a serem comparadas.
        - columns (list): Lista com os nomes das colunas a serem comparadas.
        - tolerance_percent (float): Percentual da média das diferenças de ângulo para a tolerância (padrão: 100%).

        Retorna:
        - pd.Series: Série booleana indicando se as diferenças de ângulo em cada linha estão dentro da tolerância.
        """
        if len(columns) < 2:
            raise ValueError("É necessário ao menos duas colunas para realizar a comparação.")

        if not (0 <= tolerance_percent <= 100):
            raise ValueError("O parâmetro 'tolerance_percent' deve estar entre 0 e 100.")

        # Inicializa uma série booleana com True para todas as linhas
        result = pd.Series([True] * len(df), index=df.index)

        # Lista para armazenar todas as diferenças de ângulo
        angle_differences = []

        for i in range(len(columns) - 1):
            # Calcula a diferença entre pontos consecutivos nas colunas
            delta_y1 = df[columns[i]].diff()
            delta_x1 = np.ones(len(delta_y1))  # Supondo que o espaçamento no eixo x seja constante

            delta_y2 = df[columns[i + 1]].diff()
            delta_x2 = np.ones(len(delta_y2))

            # Calcula os ângulos (em radianos) e converte para graus
            angles1 = np.degrees(np.arctan2(delta_y1, delta_x1))
            angles2 = np.degrees(np.arctan2(delta_y2, delta_x2))

            # Calcula a diferença de ângulo
            angle_diff = abs(angles1 - angles2)
            angle_differences.append(angle_diff)

        # Concatena todas as diferenças de ângulo em uma única série
        all_differences = pd.concat(angle_differences, axis=1).max(axis=1)

        # Calcula a média das diferenças de ângulo
        mean_difference = all_differences.mean()

        # Calcula a tolerância baseada na porcentagem da média
        tolerance_value = mean_difference * (tolerance_percent / 100)

        # Verifica se as diferenças estão dentro da tolerância
        result = all_differences <= tolerance_value

        return result

    @staticmethod
    def values_above_center(df: pd.DataFrame, columns: list) -> pd.Series:
        """
        Verifica se os valores em cada linha de um DataFrame estão acima do 'Centro de Força'.

        Parâmetros:
        - df (pd.DataFrame): DataFrame contendo as colunas a serem comparadas.
        - columns (list): Lista com os nomes das colunas a serem comparadas.

        Retorna:
        - pd.Series: Série booleana indicando se os valores em cada linha estão acima do 'Centro de Força'.
        """
        # Calcula o 'Centro de Força' para cada linha do DataFrame
        cof = center_of_force(df['High'], df['Open'], df['Close'], df['Low'])

        # Inicializa uma série booleana com True para todas as linhas
        result = pd.Series([True] * len(df), index=df.index)

        # Loop para verificar se os valores das colunas especificadas estão acima do 'Centro de Força'
        for col in columns:
            # Verifica se o valor na coluna está acima do 'Centro de Força'
            comparison = df[col] > cof
            # Atualiza o resultado com uma operação lógica "E" para manter as verificações anteriores
            result = result & comparison

        return result
    
    @staticmethod
    def values_below_center(df: pd.DataFrame, columns: list) -> pd.Series:
        """
        Verifica se os valores em cada linha de um DataFrame estão abaixo do 'Centro de Força'.

        Parâmetros:
        - df (pd.DataFrame): DataFrame contendo as colunas a serem comparadas.
        - columns (list): Lista com os nomes das colunas a serem comparadas.

        Retorna:
        - pd.Series: Série booleana indicando se os valores em cada linha estão abaixo do 'Centro de Força'.
        """
        # Calcula o 'Centro de Força' para cada linha do DataFrame
        cof = center_of_force(df['High'], df['Open'], df['Close'], df['Low'])

        # Inicializa uma série booleana com True para todas as linhas
        result = pd.Series([True] * len(df), index=df.index)

        # Loop para verificar se os valores das colunas especificadas estão abaixo do 'Centro de Força'
        for col in columns:
            # Verifica se o valor na coluna está abaixo do 'Centro de Força'
            comparison = df[col] < cof
            # Atualiza o resultado com uma operação lógica "E" para manter as verificações anteriores
            result = result & comparison

        return result

    @staticmethod
    def detect_highs_and_lows(df: pd.DataFrame, window: int = 1) -> pd.DataFrame:
        """
        Identifica topos (na coluna 'High') e fundos (na coluna 'Low') locais em um DataFrame de dados financeiros.

        Parâmetros:
        - df (pd.DataFrame): DataFrame contendo as colunas 'High' e 'Low' para análise.
        - window (int): Número de períodos para comparar antes e depois de cada ponto (padrão: 1).

        Retorna:
        - pd.DataFrame: DataFrame original com colunas adicionais 'Peak_High' e 'Trough_Low' indicando topos e fundos.
        """
        # Verifica se as colunas 'High' e 'Low' estão no DataFrame
        if 'High' not in df.columns or 'Low' not in df.columns:
            raise ValueError("O DataFrame deve conter as colunas 'High' e 'Low'.")

        # Inicializa as colunas 'Peak_High' e 'Trough_Low' com False
        df['Peak_High'] = False
        df['Trough_Low'] = False

        # Identifica topos e fundos locais usando rolling window
        rolling_high_max = df['High'].rolling(window=window*2+1, center=True).max()
        rolling_low_min = df['Low'].rolling(window=window*2+1, center=True).min()

        df['Peak_High'] = (df['High'] == rolling_high_max) & (df['High'] > df['High'].shift(1)) & (df['High'] > df['High'].shift(-1))
        df['Trough_Low'] = (df['Low'] == rolling_low_min) & (df['Low'] < df['Low'].shift(1)) & (df['Low'] < df['Low'].shift(-1))

        return df