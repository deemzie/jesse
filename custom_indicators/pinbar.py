import numpy as np

def pinbar(candles: np.ndarray, sensivity: float = 0.5, wick: float = 60, sequential: bool = False) -> bool:
    """
    Pinbar candlestick pattern - https://www.youtube.com/watch?v=p10LWky-SRQ
   
    Parameters
    ----------
    candles : np.ndarray 
    sensivity : float - minimum relative size of the candle in %
    wick: float - miminum size of the wick relative to the size of the candle in %
    sequential : bool - for faster computations

    Returns
    -------
    +high if the pinbar is bearish, -low if bullish, 0 otherwise

    """

    open = candles[-1, 1]
    close = candles[-1, 2]
    high = candles[-1, 3]
    low = candles[-1, 4]
    
    amplitude = high - low
    
    top_wick = high - max(open, close)
    bottom_wick = min(open,close) - low

    if top_wick / amplitude > wick / 100 and amplitude / low > sensivity / 100:
        return high
    elif bottom_wick / amplitude > wick / 100 and amplitude / low > sensivity / 100:
        return -low
    else:
        return 0
