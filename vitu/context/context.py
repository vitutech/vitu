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
from vitu.utils.date_utils import str2timestamp


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

        self.min_qty_amount = None

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
                            pre_start_date=None, end_date=None):
        ohlcv_data = get_ohlcv_data(universe, all_assets, benchmark, frequency, pre_start_date, end_date)
        self.cacher.data = ohlcv_data
        return self.cacher.data

    def history(self, symbol=None, attributes=None, bars=None, rtype='ndarray'):
        """
        :param symbol: 'BTC/USDT.binance'
        :param attributes: 'close'
        :param bars: 30
        :param rtype: 'ndarray'/'dataframe'/'list'
        :return: data
        """
        k_lines_key = symbol.split('.')[1] + '-spot-' + symbol.split('.')[0].replace('/', '').lower()
        start = self.clock.current_date - datetime.timedelta(days=bars)
        end = self.clock.current_date - datetime.timedelta(days=1)
        k_lines_history = self.cacher.get_daily_ohlcv(k_lines_key, start, end, attributes)
        if rtype == 'ndarray':
            k_lines_history = np.array(k_lines_history)
        elif rtype == 'dataframe':
            k_lines_history = k_lines_history
        elif rtype == 'list':
            # k_lines_history = k_lines_history.tolist()
            k_lines_history = np.array(k_lines_history).tolist()
        return k_lines_history

    def get_price(self, symbol):
        """
        :param symbol: "BTC/USDT.binance"
        :return:  回测：上一bar close_price
        """
        k_lines_key = symbol.split('.')[1] + '-spot-' + symbol.split('.')[0].replace('/', '').lower()
        date = self.clock.current_date
        last_bar_timestamp = str2timestamp(str(date.date()))  # date都取日级数据
        df = self.cacher.data[k_lines_key]
        last_bar_price = df.loc[(df['timestamp'] == last_bar_timestamp)]['close'].tolist()[0]
        return last_bar_price
