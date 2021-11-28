"""
https://www.youtube.com/watch?v=yXskVYp4Rps&list=LL&index=4

This is one of the best trading system of Trader's Landing.

Long: when the price is above the Supertrend and the DEMA, with the DEMA well oriented with a SL at the ST
Short: when the price is below the Supertrend and the DEMA, with the DEMA well oriented with a SL at the ST

Stop Loss: at the ST

Take profit: at a fixed R/R ratio then hold the trade till the ST changes

Filters: minimum pnl, minimum adx, and proximity from a S/R level with a atr precision

Hyperparameters: Risk both sides, R/R, TP amount in %, Indicators Settings, Threshold filters

Fixed Parameters: lookback on S/R levers set to 12 candles, minimim relative slope of the DEMA set to 0.1%

"""

from jesse.strategies import Strategy
import jesse.indicators as ta
from jesse import utils
import custom_indicators as cta
from jesse.helpers import get_candle_source

class SuperDuperSuperTrend(Strategy):
    
    def hyperparameters(self):
        return [
            {'name': 'risk_long',   'type': int, 'min': 0, 'max': 50, 'default': 10},
            {'name': 'risk_short',  'type': int, 'min': 0, 'max': 25, 'default': 0},
            {'name': 'r:r x6',      'type': int, 'min': 1, 'max': 30, 'default': 6},
            {'name': 'tp',          'type': int, 'min': 1, 'max': 100,'default': 50},
            
            {'name': 'st_atr',      'type': int, 'min': 1, 'max': 30, 'default': 20},
            {'name': 'st_period x6','type': int, 'min': 1, 'max': 40, 'default': 20},
            {'name': 'ma_type',     'type': int, 'min': 0, 'max': 39, 'default': 3},
            {'name': 'ma_period',   'type': int, 'min': 1, 'max': 200,'default': 150},
            {'name': 'adx_period',  'type': int, 'min': 1, 'max': 30, 'default': 14},
            {'name': 'atr_period',  'type': int, 'min': 1, 'max': 30, 'default': 14},
            
            {'name': 'adx_min',     'type': int, 'min': 1, 'max': 50, 'default': 14},
            {'name': 'pnl_min',     'type': int, 'min': 1, 'max': 5,  'default': 2},
        ]
    
    @property
    def anchor_candles(self):
        return self.get_candles(self.exchange, self.symbol, utils.anchor_timeframe(self.timeframe))
    
    @property
    def macro_candles(self):
        return self.get_candles(self.exchange, self.symbol, utils.anchor_timeframe(utils.anchor_timeframe(self.timeframe)))

    '''
    Indicators 
    '''
    
    @property
    def anchor_adx(self):
        return ta.adx(self.anchor_candles, self.hp['adx_period'])
    
    @property
    def atr(self):
        return ta.atr(self.candles, self.hp['atr_period'])

    @property
    def ma(self):
        ma = ta.ma(self.candles, self.hp['ma_period'], self.hp['ma_type'], sequential = True)
        trend = cta.deriv(ma).first
        return (ma[-1], trend)
    
    @property
    def supertrend(self):
        return ta.supertrend(self.candles, self.hp['st_atr'], self.hp['st_period 6x'] / 6.)
    
    '''
    Filters
    '''
    
    def filter_sr(self):
        if self.average_take_profit > self.average_entry_price:
            resistance = cta.high(get_candle_source(self.anchor_candles, 'close'), 12, -2)
            return self.average_take_profit < resistance - self.atr or self.average_entry_price > resistance + self.atr
        else:
            support = cta.low(get_candle_source(self.anchor_candles, 'close'), 12, -2)
            return self.average_take_profit > support + self.atr or self.average_entry_price < support - self.atr
    
    def filter_pnl(self):
        pnl_percentage = abs(self.average_take_profit - self.average_entry_price) / self.average_entry_price * 100
        return pnl_percentage > self.hp['pnl_min']
    
    def filter_adx(self):
        return self.anchor_adx > self.hp['adx_min']
    
    def filters(self):
        return [
            self.filter_adx,
            self.filter_pnl,
            self.filter_sr
        ]
    
    '''
    Entry
    '''

    def should_long(self) -> bool:
        if self.hp['risk_long'] != 0:
            slope_ok = self.ma[1] > 0.1 / 100
            trend_ok = self.close > self.supertrend.trend and self.close > self.ma[0]
            return slope_ok and trend_ok
        else:
            pass

    def should_short(self) -> bool:
        if self.hp['risk_short'] != 0:
            slope_ok = self.ma[1] < - 0.1 / 100
            trend_ok = self.close < self.supertrend.trend and self.close < self.ma[0]
            return slope_ok and trend_ok
        else:
            pass
    
    def should_cancel(self) -> bool:
        pass

    def go_long(self):
        if self.hp['risk_long'] != 0:
            entry = self.price
            stop = self.supertrend.trend
            tp = entry + (entry - stop) * self.hp['r:r x6'] / 6
            
            qty = cta.risk_to_qty(self.capital, self.hp['risk_long'], entry, stop, 8, self.fee_rate)
            self.buy = qty, entry
            self.stop_loss = qty, stop
            self.take_profit = [(qty * self.hp['tp'] / 100, tp)]
        else:
            pass
        

    def go_short(self):
        if self.hp['risk_short'] != 0:
            entry = self.price
            stop =  self.supertrend.trend
            tp = entry + (entry - stop) * self.hp['r:r x6'] / 6
            
            qty = cta.risk_to_qty(self.capital, self.hp['risk_short'], entry, stop, 8, self.fee_rate)
            self.sell = qty, entry
            self.stop_loss = qty, stop
            self.take_profit = [(qty * self.hp['tp'] / 100, tp)]
        else:
            pass
        
    '''
    Update
    '''
        
    def update_position(self):
        if self.supertrend.changed:
            self.liquidate()
        
    def on_reduced_position(self, order):
        pass  
