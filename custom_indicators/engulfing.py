import numpy as np

from jesse.helpers import slice_candles, np_shift

def engulfing(candles: np.ndarray, size: float = 0.5, sequential: bool = False) -> int:
    """
    Engulfing candles - https://www.youtube.com/watch?v=N5c7n2sVNic
    
    Parameters
    ----------
    candles : np.ndarray 
    body: float - default: 0.1 - minimum relative body size of the candle's body in %
    sequential : bool - for faster computations

    Returns
    -------
    1 or 2 if bullish pattern with right candle engulfing the 1 or 2 left ones, 3 if both for sequential
    -1 and -2 idem for bearish
    0 no pattern
    """
    if sequential:
    
        candles = slice_candles(candles, sequential)
        
        open = candles[:, 1]
        close = candles[:, 2]
        high = candles[:, 3]
        low = candles[:, 4]
        
        last_open = np_shift(open, 1)
        last_close = np_shift(close, 1)
        last_high = np_shift(high, 1)
        last_low = np_shift(low, 1)
        
        prev_open = np_shift(open, 2)
        prev_close = np_shift(close, 2)
        prev_high = np_shift(high, 2)
        prev_low = np_shift(low, 2)
        
        one = np.where(last_open >= last_close and close >= last_high and last_close >= open and (close - open) / open > size / 100, 1, 0)
        two = np.where(prev_open >= prev_close and close >= prev_high and last_open <= last_close and (close - prev_open) / prev_open > size / 100, 2, 0)
        mone = np.where(last_open <= last_close and close <= last_low and last_close <= open and (open - close) / open > size / 100, -1, 0)
        mtwo = np.where(prev_open <= prev_close and close <= prev_low and last_open >= last_close and (prev_open - close) / prev_open > size / 100, -2, 0)
        
        return one + two + mone + mtwo
        
    else:

        open = candles[:, 1]
        close = candles[:, 2]
        high = candles[:, 3]
        low = candles[:, 4]
        
        last_open = candles[-2, 1]
        last_close = candles[-2, 2]
        last_high = candles[-2, 3]
        last_low = candles[-2, 4]
        
        prev_open = candles[-3, 1]
        prev_close = candles[-3, 2]
        prev_high = candles[-3, 3]
        prev_low = candles[-3, 4]
        
        
        
        if last_open >= last_close and close >= last_high and last_close >= open and (close - open) / open > size / 100:
            return 1
        elif last_open <= last_close and close <= last_low and last_close <= open and (open - close) / open > size / 100:
            return -1
        elif prev_open >= prev_close and close >= prev_high and last_open <= last_close and (close - prev_open) / prev_open > size / 100:
            return 2
        elif prev_open <= prev_close and close <= prev_low and last_open >= last_close and (prev_open - close) / prev_open > size / 100:
            return -2
        else:
            return 0
