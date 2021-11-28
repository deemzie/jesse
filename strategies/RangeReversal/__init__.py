"""
https://www.youtube.com/watch?v=QRn9gaz2IXU

Long: when the price is in a S/D zone, when the supertrend is down and a candlestick reversal pattern is printed
Short: when the price is in a S/D zone, when the supertrend is up and a candlestick reversal pattern is printed

Stop Loss: the low/high of the last two candles minus 2x the atr

Take profits: at a fixed R/R ratio then at each S/D extrema or after the trend changed

Filters: none

Hyperparameters: Risk both sides, R/R, TP amount in %, Indicators Settings, Threshold filters

Fixed Parameters: the ST trail period starts at 3.5

Note: The ST trail period is the closest to the price with the right trend direction 

"""

from jesse.strategies import Strategy
import jesse.indicators as ta
from jesse import utils
import numpy as np
import custom_indicators as cta

class RangeReversal(Strategy):
    
    '''
    Parameters
    '''
    
    def __init__(self):
        super().__init__()
        self.vars['zones'] = [(3800., 4000.), (2500., 2900.),(1700., 1900.)]
        self.vars['trail_period x4'] = 14
    
    def hyperparameters(self):
        return [
            {'name': 'risk_long',      'type': int, 'min': 0,  'max': 50, 'default': 30},
            {'name': 'risk_short',     'type': int, 'min': 0,  'max': 25, 'default': 30},
            {'name': 'r:r x6',         'type': int, 'min': 1,  'max': 30, 'default': 4},
            {'name': 'tp1',            'type': int, 'min': 1,  'max': 100,'default': 25},
            {'name': 'tp2',            'type': int, 'min': 1,  'max': 100,'default': 10},
            {'name': 'tp3',            'type': int, 'min': 1,  'max': 100,'default': 25},
            {'name': 'tp4',            'type': int, 'min': 1,  'max': 100,'default': 10},
            {'name': 'tp5',            'type': int, 'min': 1,  'max': 100,'default': 20},
            
            {'name': 'st_atr',         'type': int, 'min': 1,  'max': 30, 'default': 20},
            {'name': 'st_period',      'type': int, 'min': 1,  'max': 3,  'default': 2},
            {'name': 'ma_type',        'type': int, 'min': 0,  'max': 39, 'default': 1},
            {'name': 'ma_period',      'type': int, 'min': 1,  'max': 200,'default': 14},
            {'name': 'trail_period x4','type': int, 'min': 1,  'max': 25, 'default': 14},
            {'name': 'atr_period',     'type': int, 'min': 1,  'max': 30, 'default': 14},
            {'name': 'sensivity',      'type': int, 'min': 1,  'max': 20, 'default': 5},
            {'name': 'wick',           'type': int, 'min': 50, 'max': 90, 'default': 60},
        ]
    
    '''
    Tools
    '''
    
    @property
    def anchor_candles(self):
        return self.get_candles(self.exchange, self.symbol, utils.anchor_timeframe(self.timeframe))
    
    def find_tps(self, direction, tp1):
        lines = np.sort(self.vars['zones'], axis = None)
        if direction:
            tp2 = np.min(np.where(lines > tp1, lines, np.inf))
            tp3 = np.min(np.where(lines > tp2, lines, np.inf))
            tp4 = np.min(np.where(lines > tp3, lines, np.inf))
            tp5 = np.min(np.where(lines > tp4, lines, np.inf))

        else:
            tp2 = np.max(np.where(lines < tp1, lines, 0))
            tp3 = np.max(np.where(lines < tp2, lines, 0))
            tp4 = np.max(np.where(lines < tp3, lines, 0))
            tp5 = np.max(np.where(lines < tp4, lines, 0))
        return tp2, tp3, tp4, tp5
        
    
    '''
    Indicators 
    '''
    
    @property
    def atr(self):
        return ta.atr(self.candles, self.hp['atr_period'])
    
    @property
    def supertrend(self):
        return ta.supertrend(self.candles, self.hp['st_atr'], self.hp['st_period'])
    
    @property
    def trailing(self):
        return ta.supertrend(self.candles, self.hp['st_atr'], self.vars['trail_period x4'] / 4.)
    
    '''
    Filters
    '''
    
    def filters(self):
        return [
        ]
    
    '''
    Entry
    '''

    def should_long(self) -> bool:
        if self.hp['risk_long'] != 0:
            bull_pin_ok = cta.pinbar(self.candles, self.hp['sensivity'], self.hp['wick']) > 0
            bull_eng_ok = cta.engulfing(self.candles) > 0
            trend_ok = self.close < self.supertrend.trend
            zone = False
            for (low, high) in self.vars['zones']:
                zone = zone or (low <= self.close <= high)
            return (bull_pin_ok or bull_eng_ok) and zone and trend_ok
        else:
            pass

    def should_short(self) -> bool:
        if self.hp['risk_short'] != 0:
            bear_pin_ok = cta.pinbar(self.candles, self.hp['sensivity'], self.hp['wick']) < 0
            bear_eng_ok = cta.engulfing(self.candles) < 0
            trend_ok = self.close > self.supertrend.trend
            zone = False
            for (low, high) in self.vars['zones']:
                zone = zone or (low <= self.close <= high)
            return (bear_pin_ok or bear_eng_ok) and zone and trend_ok
        else:
            pass
    
    def should_cancel(self) -> bool:
        pass

    def go_long(self):
        if self.hp['risk_long'] != 0:
            entry = self.price
            stop = cta.low(self.candles, 1) - 2 * self.atr
            tp1 = entry + (entry - stop) * self.hp['r:r x6'] / 6
            tp2, tp3, tp4, tp5 = self.find_tps(True, tp1)
            
            qty = cta.risk_to_qty(self.capital, self.hp['risk_long'], entry, stop, 8, self.fee_rate)
            self.buy = qty, entry
            self.stop_loss = qty, stop
            self.take_profit = [(qty * self.hp['tp1'] / 100, tp1),
                                (qty * self.hp['tp2'] / 100, tp2),
                                (qty * self.hp['tp3'] / 100, tp3),
                                (qty * self.hp['tp4'] / 100, tp4),
                                (qty * self.hp['tp5'] / 100, tp5)]
        else:
            pass
    

    def go_short(self):
        if self.hp['risk_short'] != 0:
            print("supertrend: ")
            print(self.supertrend.trend)
            entry = self.price
            stop =  cta.high(self.candles, 1) + 2 * self.atr
            tp1 = entry + (entry - stop) * self.hp['r:r x6'] / 6
            tp2, tp3, tp4, tp5 = self.find_tps(False, tp1)
            
            qty = cta.risk_to_qty(self.capital, self.hp['risk_short'], entry, stop, self.fee_rate)
            self.sell = qty, entry
            self.stop_loss = qty, stop
            self.take_profit = [(qty * self.hp['tp1'] / 100, tp1),
                                (qty * self.hp['tp2'] / 100, tp2),
                                (qty * self.hp['tp3'] / 100, tp3),
                                (qty * self.hp['tp4'] / 100, tp4),
                                (qty * self.hp['tp5'] / 100, tp5)]
        else:
            pass
        
    '''
    Update
    '''
        
    def update_position(self):
        if self.is_long and self.trailing.changed == 1 and self.price < self.trailing.trend and self.reduced_count > 0:
            self.liquidate()
        elif self.is_short and self.trailing.changed == 1 and self.price > self.trailing.trend and self.reduced_count > 0:
            self.liquidate()
        
    def on_reduced_position(self, order):
        #self.stopç_loss = self.average_entry_price
        self.vars['trail_period x4'] = self.hp['trail_period x4']
        if self.is_long:
            while self.price < self.trailing.trend:
                self.vars['trail_period x4'] -= 1
        elif self.is_short:
            while self.price > self.trailing.trend:
                self.vars['trail_period x4'] -= 1

            