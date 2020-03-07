'''/*---------------------------------------------------------------------------------------------
 *  Copyright (c) VituTech. All rights reserved.
 *  Licensed under the Apache License 2.0. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/
'''
from vitu.trade.order.trade import Trade
from vitu.utils.trade_utils import trade_update_position

def match_engine(current_position, context, order):
    """
    :param account: account
    :param order: order
    :return: trade
    """
    # 撮合：每撮合一笔，创建一个trade,直到order数量撮合完/撤单为止
    # 产生Trade更新对应Order和Postion
    trade = Trade(context, order['id'], order['side'],order['limit_price'], order['initial_qty'])
    order.trade_update(trade)
    # trade_update_position(current_position, trade['side'], order['instrument'], trade['price'], trade['qty'])
    trade_update_position(current_position, order['instrument'], trade)










