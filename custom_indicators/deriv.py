from collections import namedtuple

import numpy as np
import talib
from jesse.indicators.ma import ma
from jesse.helpers import get_candle_source, slice_candles, np_shift

Deriv = namedtuple('Deriv', ['first', 'second', 'third', 'double', 'triple'])

def deriv(osc: np.ndarray, sequential: bool = False) -> Deriv:
    """
    First, Second and Thrid derivative of the oscillator in parameter, 
    along with the slope from the second and third candle on the left.

    Parameters
    ----------
    osc : np.ndarray - oscillator values
    sequential : bool - for faster computation

    Returns
    -------
    Deriv

    """

    s1 = np_shift(osc, 1)
    s2 = np_shift(osc, 2)
    s3 = np_shift(osc, 3)
    
    d1 = (osc - s1) / osc
    d2 = (osc - 2*s1 + s2) / osc
    d3 = (osc - 3*s1 + 3*s2 - s3) / osc
    
    d = (osc - s2) / (2 * osc)
    t = (osc - s3) / (3 * osc)
    
    if sequential:
        return Deriv(d1, d2, d3, d, t)
    else:
        return Deriv(d1[-1], d2[-1], d3[-1], d[-1], t[-1])
