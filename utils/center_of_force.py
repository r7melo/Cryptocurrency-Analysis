import numpy as np

def center_of_force(high, open, close, low):

    body = np.maximum(open, close) - np.minimum(open, close)
    head = high - np.maximum(open, close)
    foot = np.minimum(open, close) - low

    a1 = body - head
    a0 = body - foot

    c = (high + low) / 2
    f = (a0 + a1) / 2
    cof = c + f
    
    return cof


    