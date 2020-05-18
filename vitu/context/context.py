'''/*---------------------------------------------------------------------------------------------
 *  Copyright (c) VituTech. All rights reserved.
 *  Licensed under the Apache License 2.0. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/
'''
import datetime
import numpy as np

from vitu.data.cache import DataCache
from vitu.context.clock import Clock
from vitu.utils.data_utils import get_ohlcv_data
from vitu.utils.date_utils import (
    timestamp2str,
    str2timestamp,
    datetime2timestamp
)

class Context(object):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            _instance = super(Context, cls).__new__(cls)
            cls._instance = _instance
        return cls._instance

    def __init__(self, portfolio, start_date=None, end_date=None, commission=None,
                 frequency=None, refresh_rate=None, trigger_time=None):
        """
        context包含运行时间、回测参数、回测运行所需数据 佣金等等
        """
        self.clock = Clock(start_date, end_date, frequency, refresh_rate, trigger_time)
        self.cacher = DataCache()
        self.portfolio = portfolio
        self.commission = commission
        self.commission 
        self.frequency = frequency

        self.init_portfolio_position = None
        self.init_position_total = None
        self.init_total_account_position = None

        self.completed_time = None
        self.accounts_name = None    # 记录account_name
        self.asset_varieties = None  # 记录asset种类


    def get_account(self, name):
        return self.portfolio.get_account(name)

    def current_datetime(self):
        return str(self.clock.current_date)

    def previous_datetime(self):
        return str(self.clock.previous_date)

    def prepare_data(self, universe=None, all_assets=None, benchmark=None, frequency=None,
                            pre_start_date=None, end_date=None,timezone=None):
        ohlcv_data = get_ohlcv_data(universe, all_assets, benchmark, frequency, pre_start_date, end_date,timezone)
        self.cacher.data = ohlcv_data
        # print(ohlcv_data)
        return self.cacher.data

    def history(self, symbol=None, attributes=None, bars=None, rtype='ndarray'):
        """
        :param symbol: 'BTC/USDT.binance'
        :param attributes: 'close'
        :param bars: 30
        :param rtype: 'ndarray'/'dataframe'/'list'
        :return: data
        ：frequency
        """
        k_lines_key = symbol.split('.')[1] + '-spot-' + symbol.split('.')[0].replace('/', '').lower()
        freq1=self.frequency
        if freq1 in ['d','1d','day','1day','daily']:
            end = self.clock.bars_start + self.clock.pre_bar
            start =end-bars              
        elif freq1 in ['m','1m','min','1minute']:
             end = self.clock.bars_start + self.clock.pre_bar*1440
             start =end-bars
        elif freq1 in ['5m','5min','5minutes']:
             end = self.clock.bars_start + self.clock.pre_bar*288
             start =end-bars
        k_lines_history = self.cacher.get_daily_ohlcv(k_lines_key, start, end, attributes)
        if rtype == 'ndarray':
            k_lines_history = np.array(k_lines_history)
        elif rtype == 'dataframe':
            k_lines_history = k_lines_history
        elif rtype == 'list':

            k_lines_history = np.array(k_lines_history).tolist()
        return k_lines_history

    def get_price(self, symbol):
        """
        :param symbol: "BTC/USDT.binance"
        :return:  回测：上一bar close_price
        """
        k_lines_key = symbol.split('.')[1] + '-spot-' + symbol.split('.')[0].replace('/', '').lower()
        freq1=self.frequency
        if freq1 in ['d','1d','day','1day']:
            last_bar_index =self.clock.bars_start + self.clock.pre_bar  # date取日级数据
        elif freq1 in ['m','1m','min','1minute']:
              last_bar_index = self.clock.bars_start + self.clock.pre_bar*1440
        elif freq1 in ['5m','5min','5minutes']:
             last_bar_index = self.clock.bars_start + self.clock.pre_bar*288


        df = self.cacher.data[k_lines_key]
        last_bar_price =df.loc[last_bar_index,'close'] #df.iloc[last_bar_index,:]['close']#
        return last_bar_price

    def get_depth(self,symbol_exchange):
        exchange = symbol_exchange.split('.')[1]
        symbol = symbol_exchange.split('.')[0]
        k_lines_key = exchange + '-spot-' + symbol.replace('/', '').lower()
        # date = self.clock.current_date
        freq1=self.frequency
        if freq1 in ['d','1d','day','1day']:
            last_bar_index =self.clock.bars_start + self.clock.pre_bar  # date取日级数据
        elif freq1 in ['m','1m','min','1minute']:
              last_bar_index = self.clock.bars_start + self.clock.pre_bar*1440
        elif freq1 in ['5m','5min','5minutes']:
             last_bar_index = self.clock.bars_start + self.clock.pre_bar*288

        df = self.cacher.data[k_lines_key]
        last_bar_price = df.loc[last_bar_index,'close'] #df.iloc[last_bar_index,:]['close'] 
        last_bar_qty = df.loc[last_bar_index,'volume'] #df.iloc[last_bar_index,:]['volume']# 
        if symbol=='btcusdt':
           tick1=0.5
        elif symbol=='ethusdt':
             tick1=0.05
        elif symbol=='eosusdt':
             tick1=0.001
        elif symbol=='xprusdt':
             tick1=0.0001  
        else:
             tick1=last_bar_price/10000
        depth={}
        ask1=(last_bar_price+tick1,last_bar_qty/10)
        ask2=(last_bar_price+2*tick1,last_bar_qty/10)
        ask3=(last_bar_price+3*tick1,last_bar_qty/10)
        ask4=(last_bar_price+4*tick1,last_bar_qty/10)
        ask5=(last_bar_price+5*tick1,last_bar_qty/10)
        bid1=(last_bar_price-tick1,last_bar_qty/10)
        bid2=(last_bar_price-2*tick1,last_bar_qty/10)
        bid3=(last_bar_price-3*tick1,last_bar_qty/10)
        bid4=(last_bar_price-4*tick1,last_bar_qty/10)
        bid5=(last_bar_price-5*tick1,last_bar_qty/10)
        depth['asks']=[ask1,ask2,ask3,ask4,ask5]
        depth['bids']=[bid1,bid2,bid3,bid4,bid5]

        return depth
        
