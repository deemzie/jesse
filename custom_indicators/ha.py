from collections import namedtuple

import numpy as np

from jesse.helpers import get_candle_source, slice_candles, np_shift

HeikenAshi = namedtuple('HeikenAshi', ['open', 'close', 'high', 'low', 'bull', 'bear'])

def ha(candles: np.ndarray, body: float = 0.1, size: float = 0.3, sequential: bool = False) -> HeikenAshi:
    """
    Heiken-Ashi candles - https://www.youtube.com/watch?v=p7ZYrxZo_38&t=411s
    
    Parameters
    ----------
    candles : np.ndarray 
    body: float - minimum relative size of the candle's body in %
    size - float - minimum relative size of the candle in %
    sequential : bool - for faster computations

    Returns
    -------
    HeikenAshi
    """
    
    candles = slice_candles(candles, sequential)

    open  = get_candle_source(candles, 'open')
    close = get_candle_source(candles, 'close')
    high  = get_candle_source(candles, 'high')
    low   = get_candle_source(candles, 'low')
    ohlc4 = get_candle_source(candles, 'ohlc4')

    last_open = np_shift(open, 1, open[0])
    last_close = np_shift(close, 1, close[0])
    
    ha_open  = (last_open + last_close) / 2
    ha_close = ohlc4
    ha_high  = high
    ha_low   = low
    
    big     = np.maximum(ha_open - ha_close, ha_close - ha_open) / np.maximum(ha_open, ha_close) >= body / 100
    big_ass = ha_high - ha_low / ha_low >= size / 100
    
    bull = (ha_open <= ha_low)  & big & big_ass
    bear = (ha_open >= ha_high) & big & big_ass
    

    if sequential:
        return HeikenAshi(ha_open, ha_close, ha_high, ha_low, bull, bear)
    else:
        return HeikenAshi(ha_open[-1], ha_close[-1], ha_high[-1], ha_low[-1], bull[-1], bear[-1])
    

