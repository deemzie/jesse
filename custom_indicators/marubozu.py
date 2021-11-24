import numpy as np

from jesse.helpers import slice_candles

def marubozu(candles: np.ndarray, body: float = 0.1, sensivity: float = 0, sequential: bool = False) -> bool:
    """
    Mazubozu candlestick pattern - https://www.youtube.com/watch?v=K8lhUVwP60c&t=12s
    
    Parameters
    ----------
    candles : np.ndarray
    body: float - default: 0.1 - minimum relative body size of the candle's body in %
    sensivity: float - default: 0 - maximum relative difference beween (low and close for bearish) or (high and close for bullish) in %
    sequential: bool - default: False
    
    Returns
    -------
    int | np.ndarray - +1 if bullish mrbz candle, -1 if bearish, 0 else
    """
    
    candles = slice_candles(candles, sequential)

    open = candles[:, 1]
    close = candles[:, 2]
    high = candles[:, 3]
    low = candles[:, 4]
    
    bull = np.where(open < close and (close - open) / open >= body / 100 and (high - close) / close <= sensivity / 100, 1, 0)
    bear = np.where(open > close and (open - close) / open >= body / 100 and (close - low) / close <= sensivity / 100, -1, 0)
    mrbz = np.where(bull > 0, bull, bear)

    if sequential:
        return mrbz
    else:
        return mrbz[-1]
