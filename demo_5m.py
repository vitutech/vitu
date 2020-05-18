'''/*---------------------------------------------------------------------------------------------
 *  Copyright (c) VituTech. All rights reserved.
 *  Licensed under the Apache License 2.0. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/
'''
import time
start1=time.clock()
# from vitu import ai, api, log 这一行必须导入哦
# 同样也可以import平台支持的第三方python模块，比如pandas、numpy等
from vitu import ai, log
import numpy as np
import os
#配置数据导入地址
os.environ["H5_ROOT_DIR"]="/home/john/Downloads/datah5/bundle" #"D:/datah5_m/bundle"
print(os.path.exists(os.environ["H5_ROOT_DIR"]))  #返回True，则数据导入成功
# 配置单/多账户初始持仓信息
ai.create_account(name='account1', exchange='poloniex', account_type='digital.spot', position_base=[{'asset': 'BTC', 'qty': 10},{'asset': 'USDT', 'qty': 200000}])

# initialize方法：设置策略当中会用到的参数，在handle_data方法中可以随时调用
def initialize(context):
    # 我们在这里配置MA策略使用的均线窗口大小和账户对象信息
    context.symbol = "BTC/USDT.poloniex"
    context.MA_length = 1000
    context.account_1 = context.get_account('account1')

#获取深度数据的买卖1档、买卖2档的价格和挂单量

def get_price_qty(depth):
    asks_1 = depth['asks'][0]
    asks_2 = depth['asks'][1]
    bids_1 = depth['bids'][0]
    bids_2 = depth['bids'][1]
    return asks_1,asks_2,bids_1,bids_2
# handle_data方法：主要策略逻辑，universe数据将会触发此段逻辑，例如日线历史数据或者是实时数据
# @profile
def handle_data(context):
    # 获取给定交易所的BTC/USDT历史数据
    close_price_1 = context.history('BTC/USDT.poloniex', 'close', bars=context.MA_length, rtype='ndarray')
    # 计算MA值
    MA10_1 = np.mean(close_price_1)

    # 获取binance交易所的BTC/USDT最新价格
    current_price =context.get_price(context.symbol) 
    # log.debug('当前价格:{} '.format(current_price))
    depth=context.get_depth(context.symbol)
    asks_1,asks_2,bids_1,bids_2 = get_price_qty(depth)
    # depth_info = '卖二价/量：{}/{}  卖一价/量：{}/{}  买一价/量：{}/{}  买二价/量：{}/{} '.format(
    #     asks_2[0],asks_2[1],asks_1[0],asks_1[1],bids_1[0],bids_1[1],bids_2[0],bids_2[1],)
    # log.debug(depth_info)
    asks_1_price = asks_1[0]  #卖一价
    bids_1_price = bids_1[0]  #买一价

    
    # 如果突破5000分钟均线买入0.2BTC
    if (current_price > MA10_1):
        context.account_1.buy("BTC/USDT.poloniex", asks_1_price, 0.2)
        # log.info("价格突破10日均线, 买入BTC, 价格：%d" % (asks_1_price))
    # 如果跌破5000分钟均线卖出0.2BTC
    elif (current_price< MA10_1):
        context.account_1.sell("BTC/USDT.poloniex", bids_1_price, 0.2)
        # log.info("价格跌破10日均线, 卖出BTC, 价格：%d" % (bids_1_price))


# 可以直接指定universe，或者通过筛选条件选择universe池,这里直接指定binance交易所的BTC/USDT、ETH/USDT
universe = ai.create_universe(['BTC/USDT.poloniex']) #,'ETH/USDT.binance'

# 配置策略参数如：基准、回测数据级别等
my_strategy = ai.create_strategy(
    initialize,
    handle_data,
    universe=universe,
    benchmark='csi5',
    freq='5m',
    refresh_rate=1
)

# 配置回测参数如：回测日期、所在时区、手续费率
#(默认timezone是北京时区，其他时区请手动输入，如timezone='America/New_York',timezone='Asia/Tokyo'等)
ai.backtest(
    strategy=my_strategy,
    start='2018-12-10 00:00:00',
    end='2018-12-16 00:00:00',
    commission={'taker': 0.0002, 'maker': 0.0002}
)
end1=time.clock()
print(end1-start1)

