import pandas as pd

class Indicator:

    @staticmethod
    def mean(df: pd.DataFrame, window:int):
        return df.rolling(window=window).mean() 
    
    @staticmethod
    def exponential_mean(df: pd.DataFrame, span:int):
        return df.ewm(span=span, adjust=False).mean()
    
    @staticmethod
    def compare_displaced(df: pd.DataFrame, column: str, operation: str, periods: int):
        if hasattr(df[column], operation):
            func = getattr(df[column].shift(periods).rolling(window=periods), operation)
            result = func()
            return result.shift(-periods) 
        else:
            raise ValueError(f"A operação '{operation}' não é válida para o DataFrame.")
