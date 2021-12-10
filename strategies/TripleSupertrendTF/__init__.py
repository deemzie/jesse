from jesse.strategies import Strategy
import jesse.indicators as ta
from jesse import utils


class TripleSupertrendTF(Strategy):

    def __init__(self):
        super().__init__()
        self.vars['state'] = 0
        self.vars['tp'] = [(1, 15), (2, 30), (3, 60)]
        self.vars['anchor_st'] = 0

    def hyperparameters(self):
        return [
            {'name': 'risk_entry %', 'type': int, 'min': 1, 'max': 50, 'default': 3},
            {'name': 'risk_add %',   'type': int, 'min': 1, 'max': 50, 'default': 5},

            {'name': 'r:r x6',       'type': int, 'min': 1, 'max': 30, 'default': 6},
            {'name': 'tp %',         'type': int, 'min': 1, 'max': 100, 'default': 10},

            {'name': 'st_atr',       'type': int, 'min': 1, 'max': 30, 'default': 10},
            {'name': 'st x6',        'type': int, 'min': 1, 'max': 40, 'default': 24},
            {'name': 'anchor_st x6', 'type': int, 'min': 1, 'max': 40, 'default': 24},
            {'name': 'macro_st x6',  'type': int, 'min': 1, 'max': 40, 'default': 10},
        ]

    @property
    def anchor_candles(self):
        return self.get_candles(self.exchange, self.symbol, utils.anchor_timeframe(self.timeframe))

    @property
    def macro_candles(self):
        return self.get_candles(self.exchange, self.symbol, utils.anchor_timeframe(utils.anchor_timeframe(self.timeframe)))

    @property
    def daily_candles(self):
        return self.get_candles(self.exchange, self.symbol, '1D')

    '''
    Indicators 
    '''

    @property
    def st(self):
        return ta.supertrend(self.candles, self.hp['st_atr'], self.hp['st x6'] / 6.)

    @property
    def anchor_st(self):
        return ta.supertrend(self.anchor_candles, self.hp['st_atr'], self.hp['anchor_st x6'] / 6.)

    @property
    def macro_st(self):
        return ta.supertrend(self.macro_candles, self.hp['st_atr'], self.hp['macro_st x6'] / 6.)

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
        trend_ok = self.price > self.st.trend > self.anchor_st.trend > self.macro_st.trend
        return trend_ok

    def should_short(self) -> bool:
        pass

    def should_cancel(self) -> bool:
        pass

    def go_long(self):
        entry = self.price
        stop = self.macro_st.trend
        qty = utils.risk_to_qty(self.capital, self.hp['risk_entry %'], entry, stop, 5, self.fee_rate)
        tp = entry + (entry - self.anchor_st.trend) * self.hp['r:r x6'] / 6
        
        bid1 = self.st.trend
        bid2 = self.anchor_st.trend
        qty1 = utils.risk_to_qty(self.capital, self.hp['risk_add %'], bid1, stop, 5, self.fee_rate) 
        qty2 = utils.risk_to_qty(self.capital, self.hp['risk_add %'], bid2, stop, 5, self.fee_rate) 

        self.buy = [(qty, entry), (qty1, bid1), (qty2, bid2)]
        self.stop_loss = qty + qty1 + qty2, stop
        self.take_profit = qty * self.hp['tp %'] / 100, tp

    def go_short(self):
        pass

    '''
    Update
    '''

    def update_orders(self):
        self.log(self.vars['state'])
        self.log(self._close_position_orders)
        stop = self.macro_st.trend

        if self.vars['state'] == 0:
            bid1 = self.st.trend
            bid2 = self.anchor_st.trend
            qty1 = utils.risk_to_qty(self.capital, self.hp['risk_add %'], bid1, stop, 5, self.fee_rate) 
            qty2 = utils.risk_to_qty(self.capital, self.hp['risk_add %'], bid2, stop, 5, self.fee_rate) 

            self.buy = [(qty1, bid1), (qty2, bid2)]
            self.stop_loss = self.position.qty + qty1 + qty2, stop

        if 0 < self.vars['state'] < 4:
            tp = self.st.trend + (self.st.trend - self.macro_st.trend) * self.vars['tp'][self.vars['state']-1][0]
            qty = self.position.qty * self.vars['tp'][self.vars['state']-1][1] / 100

            bid1 = self.st.trend
            bid2 = self.anchor_st.trend
            qty1 = utils.risk_to_qty(self.capital, self.hp['risk_add %'], bid1, stop, 5, self.fee_rate) 
            qty2 = utils.risk_to_qty(self.capital, self.hp['risk_add %'], bid2, stop, 5, self.fee_rate) 

            self.buy = [(qty1, bid1), (qty2, bid2)]
            self.stop_loss = self.position.qty + qty1 + qty2, stop
            self.take_profit = qty, tp

        elif self.vars['state'] == -1:
            entry = max(self.average_entry_price, self.close)
            tp = entry + (entry - self.macro_st.trend) * self.hp['r:r x6'] / 6
            qty = self.position.qty * self.hp['tp %'] / 100

            bid2 = self.anchor_st.trend
            qty2 = utils.risk_to_qty(self.capital, self.hp['risk_add %'], bid2, stop, 5, self.fee_rate) 

            self.buy = qty2, bid2
            self.stop_loss = self.position.qty + qty2, stop
            self.take_profit = qty, tp


    def update_position(self):
        self.update_orders()

    def on_reduced_position(self, order):
        self.vars['state'] += 1
        if self.vars['state'] == 0:
            self.vars['state'] += 1
        self.update_orders()

    def on_increased_position(self, order):
        self.vars['state'] += -1
        if self.vars['state'] >= 0:
            self.vars['state'] = -1
        self.update_orders()

    def after(self):
        self.vars['anchor_st'] = self.anchor_st.trend

    def on_close_position(self, order):
        self.vars['state'] = 0
