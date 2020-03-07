'''/*---------------------------------------------------------------------------------------------
 *  Copyright (c) VituTech. All rights reserved.
 *  Licensed under the Apache License 2.0. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/
'''
# from vitu import ai, api, log 这一行必须导入哦
# 同样也可以import平台支持的第三方python模块，比如pandas、numpy等
from vitu import ai, log
import numpy as np
import os
#配置数据导入地址
os.environ["H5_ROOT_DIR"]="I:/迅雷下载/opt/data/vitu/bundle"
print(os.path.exists(os.environ["H5_ROOT_DIR"]))  #返回True，则数据导入成功
# 配置单/多账户初始持仓信息
ai.create_account(name='account1', exchange='binance', account_type='digital.spot', position_base=[{'asset': 'BTC', 'qty': 10},{'asset': 'USDT', 'qty': 200000}])
ai.create_account(name='account2', exchange='binance', account_type='digital.spot', position_base=[{'asset': 'ETH', 'qty': 200}])

# initialize方法：设置策略当中会用到的参数，在handle_data方法中可以随时调用
def initialize(context):
    # 我们在这里配置MA策略使用的均线窗口大小和账户对象信息
    context.MA_length = 10
    context.account_1 = context.get_account('account1')
    context.account_2 = context.get_account('account2')

# handle_data方法：主要策略逻辑，universe数据将会触发此段逻辑，例如日线历史数据或者是实时数据
def handle_data(context):
    # 获取binance交易所的BTC/USDT历史数据
    close_price_1 = context.history('BTC/USDT.binance', 'close', bars=context.MA_length, rtype='ndarray')
    # 计算MA值
    MA10_1 = np.mean(close_price_1)

    # 获取binance交易所的BTC/USDT最新价格
    current_price_1 = context.get_price("BTC/USDT.binance")
    # 如果突破10日均线买入0.2BTC
    if (current_price_1 > MA10_1):
        context.account_1.buy("BTC/USDT.binance", current_price_1, 0.2)
        log.info("价格突破10日均线, 买入BTC, 价格：%d" % (current_price_1))
    # 如果跌破10日均线卖出0.2BTC
    elif (current_price_1 < MA10_1):
        context.account_1.sell("BTC/USDT.binance", current_price_1, 0.2)
        log.info("价格跌破10日均线, 卖出BTC, 价格：%d" % (current_price_1))


    # 获取binance交易所的ETH/USDT历史数据
    close_price_2 = context.history('ETH/USDT.binance', 'close', bars=context.MA_length, rtype='ndarray')
    # 计算MA值
    MA10_2 = np.mean(close_price_2)
    # 获取binance交易所的ETH/USDT最新价格
    current_price_2 = context.get_price("ETH/USDT.binance")
    # 如果突破10日均线买入1ETH
    if (current_price_2 > MA10_2):
        context.account_2.buy("ETH/USDT.binance", current_price_2, 1)
        log.info("价格突破10日均线, 买入ETH, 价格：%d" % (current_price_2))
    # 如果跌破10日均线卖出1ETH
    elif (current_price_2 < MA10_2):
        context.account_2.sell("ETH/USDT.binance", current_price_2, 1)
        log.info("价格跌破10日均线, 卖出ETH, 价格：%d" % (current_price_2))

# 可以直接指定universe，或者通过筛选条件选择universe池,这里直接指定binance交易所的BTC/USDT、ETH/USDT
universe = ai.create_universe(['BTC/USDT.binance','ETH/USDT.binance'])

# 配置策略参数如：基准、回测数据级别等
my_strategy = ai.create_strategy(
    initialize,
    handle_data,
    universe=universe,
    benchmark='csi5',
    freq='d',
    refresh_rate=1
)

# 配置回测参数如：回测日期、手续费率
ai.backtest(
    strategy=my_strategy,
    start='2018-11-10',
    end='2018-12-10',
    commission={'taker': 0.0002, 'maker': 0.0002}
)

