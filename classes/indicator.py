import pandas as pd
import numpy as np

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
        - pd.DataFrame: O mesmo DataFrame de entrada com duas novas colunas:
        - '9_1_Buy': Indica True quando um sinal de compra é identificado; caso contrário, False.
        - '9_1_Sell': Indica True quando um sinal de venda é identificado; caso contrário, False.
        """
        
        # Inicializa colunas para os sinais de compra e venda
        df['Setup_9_1'] = np.nan
        
        # Itera sobre o DataFrame para identificar sinais
        for i, row in df.iterrows():

            if row['Open'] < row['EMA_9'] < row['Close']:
                # Condição para sinal de compra
                df.at[i, 'Setup_9_1'] = 'Buy'

            elif row['Open'] > row['EMA_9'] > row['Close']:
                # Condição para sinal de venda
                df.at[i, 'Setup_9_1'] = 'Sell'

        return df
    
    @staticmethod
    def setup_test(df_: pd.DataFrame) -> pd.DataFrame:
        """
        Identifica sinais de operação com base na coluna 'Setup_9_1' e avalia o sucesso da operação.
        
        Parâmetros:
        - df_ (pd.DataFrame): DataFrame contendo a coluna 'Setup_9_1' e dados históricos de preço.
        
        Retorna:
        - pd.DataFrame: DataFrame com uma nova coluna 'Operation' indicando se a operação foi 'Gain' ou 'Loss'.
        """
        df = df_.copy()

        # Inicializa a coluna para os sinais de operação como do tipo string
        df['Operation'] = np.nan
        df['Operation'] = df['Operation'].astype('object')  # Garantir que a coluna é do tipo object

        # Itera sobre o DataFrame para identificar sinais e avaliar a operação
        for i in range(1, len(df) - 10): 
            if not pd.isna(df.iloc[i]['Setup_9_1']):
                operation = df.iloc[i]['Setup_9_1']

                if operation == 'Buy':
                    loss = df.iloc[i-1]['Low']
                    gain = df.iloc[i+1]['Open'] + (df.iloc[i+1]['Open'] - loss) * 5

                    for ii in range(i+1, i+10):
                        if ii >= len(df):  # Garantir que o índice está dentro dos limites
                            break
                        if df.iloc[ii]['Low'] <= loss:
                            df.at[i, 'Operation'] = 'Loss'
                            break
                        elif df.iloc[ii]['High'] >= gain:
                            df.at[i, 'Operation'] = 'Gain'
                            break

                elif operation == 'Sell':
                    loss = df.iloc[i-1]['High']
                    gain = df.iloc[i+1]['Open'] - (loss - df.iloc[i+1]['Open']) * 5

                    for ii in range(i+1, i+10):
                        if ii >= len(df):  # Garantir que o índice está dentro dos limites
                            break
                        if df.iloc[ii]['High'] >= loss:
                            df.at[i, 'Operation'] = 'Loss'
                            break
                        elif df.iloc[ii]['Low'] <= gain:
                            df.at[i, 'Operation'] = 'Gain'
                            break
                
        return df
