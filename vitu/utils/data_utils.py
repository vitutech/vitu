'''/*---------------------------------------------------------------------------------------------
 *  Copyright (c) VituTech. All rights reserved.
 *  Licensed under the Apache License 2.0. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/
'''
from vitu.data.data import get_data


def get_ohlcv_data(universe, all_assets, benchmark, frequency, pre_start_date, end_date):
    ohlcv_data = dict()
    freq = '1d' if frequency == 'd' else '1m'
    for univ in universe:
        exchange = univ.split('.')[1]  # binance
        symbol = univ.split('.')[0].replace('/', '').lower()  # btcusdt
        symbol_cmc = symbol.replace('usdt', 'usd')
        k_lines_key = exchange + '-spot-' + symbol
        cmc_key = 'cmc-spot-' + symbol.replace('usdt', 'usd')
        ohlcv_data[k_lines_key] = get_data(exchange, symbol, freq, pre_start_date, end_date)
        ohlcv_data[cmc_key] = get_data('cmc', symbol_cmc, freq, pre_start_date, end_date)
    ohlcv_data['cmc-spot-usdtusd'] = get_data('cmc', 'usdtusd', freq, pre_start_date, end_date)
    if benchmark == 'btc':
        ohlcv_data['chainext-index-' + benchmark] = get_data('cmc', 'btcusd', freq, pre_start_date, end_date)
    else:
        ohlcv_data['chainext-index-' + benchmark] = get_data('chainext', benchmark, freq, pre_start_date, end_date)
    # 添加除universe里asset的cmc数据
    for asset in all_assets:
        symbol = '{}usd'.format(asset)
        cmc_key = 'cmc-spot-{}usd'.format(asset)
        if cmc_key not in ohlcv_data.keys():
            ohlcv_data[cmc_key] = get_data('cmc', symbol, freq, pre_start_date, end_date)
    return ohlcv_data

def get_btc_usdt_cost(asset, date):
    if asset == 'btc':
        avg_cost_btc = 1
        temp_getprice=get_data('binance', 'btcusdt', '1d', date,date)  # 默认都以binance为主
        avg_cost_usdt =temp_getprice.close[0]
        # avg_cost_usdt = get_price('binance', 'btcusdt', '1d', date)  # 默认都以binance为主
    elif asset == 'usdt':
        temp_getprice=get_data('binance', 'btcusdt', '1d', date,date)  # 默认都以binance为主
        avg_cost_btc=1/temp_getprice.close[0]
        # avg_cost_btc = 1 / get_price('binance', 'btcusdt', '1d', date)
        avg_cost_usdt = 1
    else:
        temp_getprice1=get_data('binance', '{}btc'.format(asset), '1d', date,date) 
        temp_getprice2=get_data('binance', '{}usdt'.format(asset), '1d', date,date) 
        avg_cost_btc=temp_getprice1.close[0]
        avg_cost_usdt=temp_getprice2.close[0]
        # avg_cost_btc = get_price('binance', '{}btc'.format(asset), '1d', date)
        # avg_cost_usdt = get_price('binance', '{}usdt'.format(asset), '1d', date)
    return avg_cost_btc,avg_cost_usdt






