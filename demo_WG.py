import time
start1=time.clock()
import math
import time
from vitu import ai, log
import numpy as np
import os
#配置数据导入地址
os.environ["H5_ROOT_DIR"]="/home/john/Downloads/datah5/bundle"
print(os.path.exists(os.environ["H5_ROOT_DIR"]))  #返回True，则数据导入成功
# 配置单/多账户初始持仓信息
ai.create_account(name='account1', exchange='binance', account_type='digital.spot', position_base=[{'asset': 'USDT', 'qty': 50000}])

def initialize(context):
    context.symbol = "BTC/USDT.binance"
    context.grids = []
    context.qty = 0.3
    context.grid_direction = 1             # -1向下开网格btc 1向上开网格usdt
    context.grid_num = 15                  # 网格数量
    context.set_sep = 40                   # 网格间距
    context.cover_spread = 80              # 网格平仓价差
    context.stop_loss_times = 0            # 止损次数
    context.stop_profit_times = 0          # 止盈次数
    context.account = context.get_account('account1')

def get_price_qty(depth):
    asks_1 = depth['asks'][0]
    asks_2 = depth['asks'][1]
    bids_1 = depth['bids'][0]
    bids_2 = depth['bids'][1]
    return asks_1,asks_2,bids_1,bids_2

# 开网格节点
def open_grid(grids, direction, asks_1, bids_1, set_sep):
    if len(grids) == 0:
        return True
    if direction == 1:
        actual_sep = bids_1 - grids[-1]['trigger_price']
        if actual_sep > set_sep:
            return True
    if direction == -1:
        actual_sep = asks_1 - grids[-1]['trigger_price']
        if actual_sep < -set_sep:
            return True
    else:
        return False

def push_grid(grids, trigger_price, cover_price):
    grids.append({'trigger_price': trigger_price,
                  'cover_price': cover_price})

def stop_profit(grids, direction, asks_1, bids_1):
    # 平仓，网格数大于0
    if len(grids) > 0:
        if direction == 1 and asks_1 < grids[-1]['cover_price']:
            return True
        if direction == -1 and bids_1 > grids[-1]['cover_price']:
            return True
        else:
            return False
    return False

def stop_loss(grids, grid_num):
    if len(grids) > grid_num:
        return True
    else:
        return False

def handle_data(context):
    info_str = '网格数量：{}  止盈次数：{}  止损次数：{}'.format(
        len(context.grids),context.stop_profit_times,context.stop_loss_times)
    # log.info(info_str)
    # log.info(context.grids)

    depth = context.get_depth(context.symbol)
    asks_1,asks_2,bids_1,bids_2 = get_price_qty(depth)
    # depth_info = '卖二价/量：{}/{}  卖一价/量：{}/{}  买一价/量：{}/{}  买二价/量：{}/{} '.format(
    #     asks_2[0],asks_2[1],asks_1[0],asks_1[1],bids_1[0],bids_1[1],bids_2[0],bids_2[1],)
    # log.info(depth_info)
    price = context.get_price(context.symbol)
    # log.info('当前价格:{} '.format(price))

    asks_1_price = asks_1[0]
    bids_1_price = bids_1[0]
    if open_grid(context.grids, context.grid_direction, asks_1_price, bids_1_price, context.set_sep):
        # 做多网格
        if context.grid_direction == 1:
            context.account.sell(context.symbol, bids_1_price, context.qty)
            cover_price = bids_1_price - context.cover_spread
            push_grid(context.grids, bids_1_price, cover_price)
        # 做空网格
        if context.grid_direction == -1:
            context.account.buy(context.symbol, asks_1_price, context.qty)
            cover_price = asks_1_price + context.cover_spread
            push_grid(context.grids, asks_1_price, cover_price)

    # 最后一个网格止盈
    if stop_profit(context.grids, context.grid_direction, asks_1_price, bids_1_price):
        if context.grid_direction == 1:
            context.account.buy(context.symbol, asks_1_price, context.qty)
        if context.grid_direction == -1:
            context.account.sell(context.symbol, bids_1_price, context.qty)
        context.stop_profit_times += 1
        context.grids.pop()

    # 创建网格数量超过指定数量，第一个网格止损
    if stop_loss(context.grids, context.grid_num):
        if context.grid_direction == 1:
            context.account.buy(context.symbol, asks_1_price, context.qty)
        if context.grid_direction == -1:
            context.account.sell(context.symbol, bids_1_price, context.qty)
        context.stop_loss_times+= 1
        del context.grids[0]

universe = ai.create_universe(['BTC/USDT.binance'])

my_strategy = ai.create_strategy(
    initialize,
    handle_data,
    universe=universe,
    benchmark='csi5',
    freq='1m',
    refresh_rate=1
)

ai.backtest(
    strategy=my_strategy,
    start='2018-10-10 00:00:00',
    end='2018-10-15 00:00:00',
    commission={'taker': 0.0002, 'maker': 0.0002}
)   
end1=time.clock()
print(end1-start1)