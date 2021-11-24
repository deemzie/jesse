"""
These are the functions I use as custom indicators but which rather behave like utils or helpers functions
Don't forget to import them all in __init___
"""

import numpy as np
from jesse.helpers import get_candle_source, slice_candles, np_shift

def last_signal(osc, signal, range_down, range_up):
    """
    Parameters
    ----------
    os c: np.ndarray - oscillator's values
    signal : np.ndarray - boolean array of the signal 
    range_down : int - start of the window
    range_up : int - end of the window
    
    Returns
    -------
    distance from current time where the last signal was given + value of the indicator at the time of the signal

    """
   
    window = signal[-range_up: -range_down]
    lasts = np.where(window)[0]
    if len(lasts) == 0:
        return (np.nan, np.nan)
    else:
        distance = min(range_up, len(window)) + range_down - lasts[-1] - 1
        return (distance, osc[-distance-1])
    
def last_signal_in_range(osc, signal, range_down, range_up):
    """ aggregates last_signal result in an array """
    return np.array([last_signal(np_shift(osc, i), np_shift(signal, i, False), range_down, range_up) for i in range(len(signal)-1,-1,-1)]).T

    
def low(array, past: int = 20, future: int = 0, source: str = 'low', sequential = False):
    """
    Parameters
    ----------
    array : np.ndarray - prices or indicators values
    past : int - how far to look in the past 
    future : int - how far to look in the future (the function can be called at current time but with an offset)
    source : str - if prices values given in parameters
    sequential : bool - for faster computations

    Returns
    -------
    the low of the price source or the indicator passed in parameters on the given window

    """
    if len(array.shape) == 1:
        lows = np_shift(array, -future)
    elif len(array.shape) == 2:
        array = slice_candles(array, sequential)
        array = get_candle_source(array, source)
        lows = np_shift(array, -future)
    for i in range(-past,future):
        lows = np.minimum(lows, np_shift(array, -i))
    if sequential:
        return lows
    else:
        return lows[-1]

def pivotlow(array, past, future):
    """ np.ndarray of bool, true if array value is the low in the window """ 
    return array == low(array, past, future)

def high(array, past: int = 20, future: int = 0, source: str = 'high', sequential = False):
    """
    Parameters
    ----------
    array : np.ndarray - prices or indicators values
    past : int - how far to look in the past 
    future : int - how far to look in the future (the function can be called at current time but with an offset)
    source : str - if prices values given in parameters
    sequential : bool - for faster computations

    Returns
    -------
    the high of the price source or the indicator passed in parameters on the given window

    """
    if len(array.shape) == 1:
        highs = np_shift(array, -future)
    elif len(array.shape) == 2:
        array = slice_candles(array, sequential)
        array = get_candle_source(array, source)
        highs = np_shift(array, -future)
    for i in range(-past,future):
        highs = np.maximum(highs, np_shift(array, -i))
    if sequential:
        return highs
    else:
        return highs[-1]

def pivothigh(array, past, future):
    """ np.ndarray of bool, true if array value is the high in the window """ 
    return array == high(array, past, future)

def zoom_timeframe(timeframe):
    """ inverse of anchor_timeframe  """
    zoom = {'3m': '1m', '5m': '1m', '15m': '3m', '30m': '5m', '45m': '5m', '1h': '15m', '2h': '30m', '3h': '45m', '4h': '1h', '6h': '1h', '8h': '2h', '12h': '2h', '1D': '4h', '3D': '12h', '1W': '1D'}
    return zoom[timeframe]

def risk_to_qty(capital: float, risk_per_capital: float, entry_price: float, stop_loss_price: float, precision: int = 8, fee_rate: float = 0) -> float:
    """ same as jesse.utils.risk_to_qty but without size limitation to wallet balance """
    risk_per_qty = abs(entry_price - stop_loss_price)
    size = risk_to_size(capital, risk_per_capital, risk_per_qty, entry_price) * (1 - fee_rate * 3)
    return size_to_qty(size, entry_price, precision=precision, fee_rate=fee_rate)

def risk_to_size(capital_size: float, risk_percentage: float, risk_per_qty: float, entry_price: float) -> float:
    """ same as jesse.utils.risk_to_size but without size limitation to wallet balance """
    if risk_per_qty == 0:
        raise ValueError('risk cannot be zero')
    return ((risk_percentage / 100 * capital_size) / risk_per_qty) * entry_price

def size_to_qty(position_size: float, entry_price: float, precision: int = 3, fee_rate: float = 0) -> float:
    """ same as jesse.utils.size_to_qty but without size limitation to wallet balance """
    return position_size / entry_price * (1 - fee_rate * 3)


