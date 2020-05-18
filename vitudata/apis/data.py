'''/*---------------------------------------------------------------------------------------------
 *  Copyright (c) VituTech. All rights reserved.
 *  Licensed under the Apache License 2.0. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/
'''
#!/usr/bin/env python
#coding:utf-8

'''
取数据相关接口
'''
import datetime
import json
# import redis
import h5py
import sys

import pytz
import six
import numpy as np
import pandas as pd

from vitudata.apis import data_utils
from vitudata.config import Config
from vitudata.exceptions import ParamsError, SymbolNotSupported, InternalError
import os

ochlv_type = np.dtype(
    [('timestamp', 'uint64'), ('open', 'float_'), ('high', 'float_'), ('low', 'float_'), ('close', 'float_'),
     ('volume', 'float_')])

__all__ = [
    'get_bars',
]

def get_path(exchange, symbol, freq, year):
    dir = Config.h5_root_dir() + '/' + exchange.lower() + '/' + freq.lower() + '/' + symbol.replace('/', '')
    # dir = dir.lower()
    if not os.path.exists(dir):
        os.makedirs(dir, 0o755)
    return dir + '/' + str(year)

def __check_symbol_exists(symbol, exchange, freq):
    dir = Config.h5_root_dir() + '/' + exchange.lower()+ '/' + freq.lower() + '/' + symbol.replace('/', '')
    # dir = dir.lower()
    # print(dir)
    return os.path.exists(dir)


def __get_pos_of_h5(dt, frequency):
    if frequency == '1d':
        return dt.timetuple().tm_yday -1
    if frequency == '1m':
        return (dt.timetuple().tm_yday -1) * 1440 + dt.timetuple().tm_hour * 60  + dt.timetuple().tm_min
    if frequency == '5m':
        return (dt.timetuple().tm_yday - 1) * 288 + (dt.timetuple().tm_hour) * 12 + int(dt.timetuple().tm_min / 5)


def __get_redis_key(exchange, symbol, frequency):
    return f'ohlcv_{frequency}_{exchange}_{symbol.replace("/","").lower()}'


def get_bars(symbol, exchange, start_date=None, end_date=None, frequency='1d', timezone=1, count=None):
    '''
    获取标的行情数据

    Args:
        symbol: 标的
        exchange: 交易所
        start_date: 开始日期
        end_date: 结束日期
        frequency: 周期
        count: 取数据条数
    Returns:
        numpy.ndarray
    '''
    if count is not None and start_date is not None:
        raise ParamsError("get_bars 不能同时指定 start_date 和 count 两个参数")
    if not __check_symbol_exists(symbol, exchange, frequency):
        raise SymbolNotSupported(f"交易所{exchange}频率为{frequency}的交易对{symbol}不在支持范围内")
    now = datetime.datetime.now(pytz.timezone('utc'))
    differ=28800
    if timezone==1 or timezone is None:
        differ=28800 #默认北京与UTC的时差
    elif isinstance(timezone,str):
        now_utc=datetime.datetime.now(pytz.timezone('utc')).strftime('%Y-%m-%d %H:%M:%S')
        now_loacl=datetime.datetime.now(pytz.timezone(timezone)).strftime('%Y-%m-%d %H:%M:%S') #本地时间格式
        localstamp=datetime.datetime.strptime(now_loacl,'%Y-%m-%d %H:%M:%S').timestamp()
        utcstamp=datetime.datetime.strptime(now_utc,'%Y-%m-%d %H:%M:%S').timestamp()
        differ=round(localstamp-utcstamp)  #选取的timezone时间和utc时间的差（stamp按秒计算的差值）
    if end_date is None:
        end_dt = now
    else:
        end_dt = data_utils.convert_dt(end_date)

    # 根据频率确定准确时间
    if frequency == '1d':
        end_dt = end_dt.replace(hour=0, minute=0, second=0, microsecond=0)
    if frequency == '1m':
        end_dt = end_dt.replace(second=0, microsecond=0)
    if frequency == '5m':
        minu = end_dt.minute
        end_dt = end_dt.replace(minute=int(minu/5) * 5, second=0, microsecond=0)

    if start_date is None:
        if count is None:
            count = 100
        # 根据end_dt, count, frequency, 计算准确的start_dt
        if frequency == '1d':
            start_dt = end_dt - datetime.timedelta(days=count-1)
        if frequency == '1m':
            start_dt = end_dt - datetime.timedelta(minutes=count-1)
        if frequency == '5m':
            start_dt = end_dt - datetime.timedelta(minutes=(count-1)*5)
    else:
        start_dt = data_utils.convert_dt(start_date)
        if frequency == '1d':
            start_dt = start_dt.replace(hour=0, minute=0, second=0, microsecond=0)
        if frequency == '1m':
            start_dt = start_dt.replace(second=0, microsecond=0)
        if frequency == '5m':
            minu = start_dt.minute
            start_dt = start_dt.replace(minute=int(minu / 5) * 5, second=0, microsecond=0)

    start = start_dt
    result = None
    while True:
        end = start.replace(month=12, day=31)
        if frequency == '1m':
            end = end.replace(hour=23, minute=59)
        if frequency == '5m':
            end = end.replace(hour=23, minute=55)

        if end>end_dt:
            end = end_dt
        # read data bewteen start and end
        path = get_path(exchange, symbol, frequency, start.year)
        if os.path.exists(path):
            retry = 3
            i = __get_pos_of_h5(start, frequency)
            j = __get_pos_of_h5(end, frequency)
            while retry:
                try:
                    f = h5py.File(path, mode='r', libver='latest', swmr=True)
                    data = f['ohlcv'][i:j+1]
                    break
                except Exception as e:
                    retry -=1
                    if not retry:
                        raise InternalError("无法获取到数据，请稍后再试")
            if type(data) is np.ndarray and len(data) > 0:
                if result is None:
                    result = data
                else:
                    result = np.concatenate((result,data),axis=0)
        if end >= end_dt:
            break
        start = end.replace(hour=0, minute=0) + datetime.timedelta(days=1)
    result = result[result['timestamp'] >= 0] #保留timestamp 和ohlcv为0的那些行

    result['timestamp']=result['timestamp']-differ
    #换回成本地时间的时间戳
   

    # 判断是否有数据在redis中而不在h5中
    # if len(result) > 0:
    #     min_t = result[-1][0]
    # else:
    #     min_t = start_dt.timestamp() -1
    # max_t = end_dt.timestamp()
    # if (frequency == '1m' or frequency == '5m') and (now - end_dt).total_seconds() < 7200:
    #     #最近2小时的数据在redis中
    #     if frequency == '5m':
    #         max = 24
    #     else:
    #         max = 120
    #     rkey = __get_redis_key(exchange, symbol, frequency)
    #     r = redis.Redis(host=Config.redis_host(), port=Config.redis_port())
    #     data = r.lrange(rkey, 0, max)
    #     jd = [json.loads(i) for i in data]
    #     jd = [(int(i['t']), float(i['o']), float(i['h']), float(i['l']), float(i['c']), float(i['v'])) for i in jd]
    #     npdata = np.asarray(jd, dtype=ochlv_type)
    #     npdata = npdata[npdata['timestamp'] > min_t]
    #     npdata = npdata[npdata['timestamp'] <= max_t]
    #     result = np.concatenate((result, npdata), axis=0)
    return result

if __name__ == '__main__':
    print(get_bars('btcusdt', 'binance', frequency='1d', start_date='2019-12-30', end_date='2020-1-3'))



