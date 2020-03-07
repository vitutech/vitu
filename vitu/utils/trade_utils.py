'''/*---------------------------------------------------------------------------------------------
 *  Copyright (c) VituTech. All rights reserved.
 *  Licensed under the Apache License 2.0. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/
'''
# from vitu import API, Config
from vitu.trade.position.spot_position import SpotPosition
from vitu.utils.data_utils import get_btc_usdt_cost


def order_update_position(context, current_position, side, exchange, symbol, price, qty):
    """
    产生Order更新对应Postion
    :param side: buy/sell
    :param exchange: binance
    :param symbol: BTC/USDT
    :param price: 价格
    :param qty: 数量
    :return:
    """
    base_currency = symbol.split('/')[0].lower()   # btc  基础货币
    quote_currency = symbol.split('/')[1].lower()  # usdt 计价货币
    if base_currency not in context.asset_varieties:
        context.asset_varieties.append(base_currency)
    if quote_currency not in context.asset_varieties:
        context.asset_varieties.append(quote_currency)

    if base_currency not in current_position.keys():
        # 计算初始持仓成本
        avg_cost_btc, avg_cost_usdt = get_btc_usdt_cost(base_currency, context.current_datetime())
        position = SpotPosition('spot', base_currency, avg_cost_btc=avg_cost_btc, avg_cost_usdt=avg_cost_usdt)
        position.context = context
        current_position[base_currency] = position

    if quote_currency not in current_position.keys():
        # 计算初始持仓成本
        avg_cost_btc, avg_cost_usdt = get_btc_usdt_cost(quote_currency, context.current_datetime())
        position = SpotPosition('spot', quote_currency, avg_cost_btc=avg_cost_btc, avg_cost_usdt=avg_cost_usdt)
        position.context = context
        current_position[quote_currency] = position
    current_position[base_currency].order_update('base', side, price, qty)
    current_position[quote_currency].order_update('quote', side, price, qty)

def trade_update_position(current_position, symbol, trade):
    """
    产生Trade更新对应Postion
    """
    base_currency = symbol.split('/')[0].lower()   # btc  基础货币
    quote_currency = symbol.split('/')[1].lower()  # usdt 计价货币
    current_position[base_currency].trade_update('base', trade)
    current_position[quote_currency].trade_update('quote', trade)
    # 更新open_cost开仓成本
    current_position[base_currency].trade_update_cost('base', trade, current_position[quote_currency])
    current_position[quote_currency].trade_update_cost('quote', trade, current_position[base_currency])


