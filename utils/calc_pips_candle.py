def calc_pips_candle(preco_abertura: float, preco_fechamento: float, casas_decimais: int) -> float:
    """
    Calcula a quantidade de pips gerados por um candle no mercado Forex.
    
    Parâmetros:
    - preco_abertura (float): O preço de abertura do candle.
    - preco_fechamento (float): O preço de fechamento do candle.
    - casas_decimais (int): O número de casas decimais usado no par de moedas (2 para pares com JPY, 4 para a maioria dos outros pares).
    
    Retorna:
    - float: A quantidade de pips gerados.
    """
    # Calcula a variação de preço
    variacao_preco = preco_fechamento - preco_abertura
    
    # Determina o fator multiplicador com base nas casas decimais
    multiplicador = 10 ** casas_decimais
    
    # Calcula a quantidade de pips
    quantidade_pips = variacao_preco * multiplicador
    
    # Retorna o valor absoluto de quantidade_pips para evitar valores negativos
    return abs(quantidade_pips)
