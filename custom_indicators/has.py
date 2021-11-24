from collections import namedtuple

import numpy as np
import talib

from jesse.helpers import slice_candles, np_shift

HeikenAshiSmoothed = namedtuple('HeikenAshiSmoothed', ['open', 'close', 'high', 'low', 'green'])

def has(candles: np.ndarray, len1: int = 12, len2: int = 3, sequential: bool = False) -> HeikenAshiSmoothed:
    """
    Heiken-Ashi Smoothed indicator - https://www.youtube.com/watch?v=Y2Akd_WMKY4 and https://fr.tradingview.com/script/ROokknI2-Smoothed-Heiken-Ashi-Candles-v1/

    Parameters
    ----------
    candles : np.ndarray 
    len1 : int 
    len2 : int
    sequential : bool

    Returns
    -------
    HeikenAshiSmoothed

    """
    
    candles = slice_candles(candles, sequential)

    open = candles[:, 1]
    close = candles[:, 2]
    high = candles[:, 3]
    low = candles[:, 4]

    o = talib.EMA(open, len1)
    c = talib.EMA(close, len1)
    h = talib.EMA(high, len1)
    l = talib.EMA(low, len1)

    haclose = (o+h+l+c)/4
    haopen = (np_shift(o, 1, candles[0, 1]) + np_shift(c, 1, candles[0, 2])) / 2
    hahigh = np.maximum(h, np.maximum(haopen, haclose))
    halow = np.minimum(l, np.minimum(haopen, haclose))

    o2 = talib.EMA(haopen, len2)
    c2 = talib.EMA(haclose, len2)
    h2 = talib.EMA(hahigh, len2)
    l2 = talib.EMA(halow, len2)

    if sequential:
        return HeikenAshiSmoothed(o2, c2, l2, h2, o2 < c2)
    else:
        return HeikenAshiSmoothed(o2[-1], c2[-1], l2[-1], h2[-1], o2[-1] < c2[-1])

