'''/*---------------------------------------------------------------------------------------------
 *  Copyright (c) VituTech. All rights reserved.
 *  Licensed under the Apache License 2.0. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/
'''
import time
import datetime

from vitu.utils.date_utils import (
    str2datetime,
    str2timestamp,
    datetime2timestamp
)

class Clock(object):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            _instance = super(Clock, cls).__new__(cls)
            cls._instance = _instance
        return cls._instance

    def __init__(self, start_date=None, end_date=None, frequency=None, refresh_rate=None, trigger_time=None):
        """
        :param start_date: 初始日期
        :param end_date: 结束日期
        """
        self._str_date = start_date + ' ' + trigger_time[0] if trigger_time else start_date
        self._current_date = str2datetime(self._str_date)   # 当前日期 datetime
        self._previous_date = None
        self._current_timestamp = None                       # 当前日期 时间戳
        self._end_timestamp = str2timestamp(end_date)     # 结束日期 时间戳
        self._bars = 0                                       # 开始bars数量
        self._run_start = time.time()                        # 记录run运行时间
        self._run_end = None

        self._frequency = frequency
        self._refresh_rate = refresh_rate

    @property
    def bars(self):
        return self._bars

    @bars.setter
    def bars(self, bars):
        self._bars = bars

    @property
    def current_date(self):
        return self._current_date

    @current_date.setter
    def current_date(self, current_date):
        self._current_date = current_date

    @property
    def previous_date(self):
        if self._frequency in ['d','day','daily']:
            # self._previous_date = self._current_date - datetime.timedelta(days=self._refresh_rate)
            self._previous_date = self._current_date - datetime.timedelta(days=1)
        elif self._frequency in ['m','min','minute']:
            self._previous_date = self._current_date - datetime.timedelta(minutes=1)
        return self._previous_date

    @property
    def current_timestamp(self):
        self._current_timestamp = datetime2timestamp(self._current_date)
        return self._current_timestamp

    @property
    def end_timestamp(self):
        return self._end_timestamp

    @property
    def run_start(self):
        return self._run_start

    @property
    def run_end(self):
        return self._run_end

    @run_end.setter
    def run_end(self, timestamp):
        self._run_end = timestamp


    def reset_bars(self):
        self._bars = 0

    def next(self):
        if self._frequency in ['d','day','daily']:
            # self._current_date += datetime.timedelta(days=self._refresh_rate)
            self._current_date += datetime.timedelta(days=1)
        elif self._frequency in ['m','min','minute']:
            self._current_date += datetime.timedelta(minutes=1)
        self._bars += 1


