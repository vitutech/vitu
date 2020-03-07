'''/*---------------------------------------------------------------------------------------------
 *  Copyright (c) VituTech. All rights reserved.
 *  Licensed under the Apache License 2.0. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/
'''
from vitu.data.static.min_order import min_order

def get_min_order(exchange,symbol):
    if exchange == 'poloniex':
        exchange = 'binance'
    min_order_qty = min_order[exchange][symbol.upper()]['min_order_qty']
    min_order_amount = min_order[exchange][symbol.upper()]['min_order_amount']
    return min_order_qty,min_order_amount

if __name__ == '__main__':
    # baseAsset            基础货币 BTC
    # quoteAsset           计价货币 USDT
    # maxMarketOrderQty    最大市价单数量
    # minMarketOrderQty    最小市价单数量
    # minTickSize          （最下价格波动）
    # minOrderValue        最小下单金额 10USDT
    # minTradeAmount       最小下单数量 0.000001BTC
    symbols = ['btc/usdt','eth/usdt','eos/usdt','xrp/usdt','eth/btc']
    for symbol in symbols:
        min_order_qty,min_order_amount = get_min_order('binance',symbol)
        print(min_order_qty,min_order_amount)








