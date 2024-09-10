import pandas as pd

class Indicator:

    @staticmethod
    def mean(df: pd.DataFrame, window:int):
        return df.rolling(window=window).mean() 
    
    def exponential_mean(df: pd.DataFrame, span:int):
        return df.ewm(span=span, adjust=False).mean()