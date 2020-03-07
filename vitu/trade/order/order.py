'''/*---------------------------------------------------------------------------------------------
 *  Copyright (c) VituTech. All rights reserved.
 *  Licensed under the Apache License 2.0. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/
'''
from uuid import uuid1

class Order(object):
    __slots__ = [
        'context',
        'id',
        'account',
        'instrument',
        'exchange',
        'asset_class',
        'side',
        'type',
        'limit_price',
        'avg_price',
        'initial_qty',
        'filled_qty',
        'filled_amount',
        '_commission',
        'status',
        'create_time',
        'complete_time',
        'trades'
    ]
    def __init__(self, context, name, symbol, exchange, asset_class, side, type, price, qty):
        """
        :param name: 'spot_account'
        :param symbol: 'btc/usdt'
        :param exchange: 'binance'
        :param asset_class: 'spot' | 'contract'
        :param side: 'sell' | 'buy' | 'open_long' | 'close_long'...
        :param type: 'limit' | 'market'
        :param price: 价格
        :param qty: 数量
        """
        self.context = context
        self.id = str(uuid1())
        self.account = name
        self.instrument = symbol.lower()
        self.exchange = exchange
        self.asset_class = asset_class
        self.side = side
        self.type = type
        self.limit_price = price       # 限价单
        self.avg_price = None
        self.initial_qty = qty      # 下单数量, 以btc/usdt为例, 如果是限价,买卖均是btc的数量, 如果是市价,卖是btc数量,买是usdt数量
        self.filled_qty = None         # 成交数量, 以btc/usdt为例, 无论什么方向,都是btc的数量
        self.filled_amount = None      # 成交金额, 无论什么方向,都是usdt的数量
        self._commission = 0
        self.status = 'Pending'        # 'Filled' | 'Partial_Filled' | 'Pending' | 'Cancelled' | 'Withdrawn'
        self.create_time = context.current_datetime()
        self.complete_time = None
        self.trades = list()

    @property
    def commission(self):
        """
        :return: 成交手续费
        """
        return self._commission

    @commission.setter
    def commission(self, value):
        """
        :return: 成交手续费
        """
        if not value:
            value = 0
        self._commission += value

    def trade_update(self, trade):
        if not self.avg_price:
            self.avg_price = 0
        if not self.filled_qty:
            self.filled_qty = 0
        self.avg_price = trade['price']
        self.filled_qty = trade['qty']
        self.filled_amount = self.avg_price * self.filled_qty
        self.commission = trade['commission']
        self.status = 'Filled'
        self.complete_time = self.context.current_datetime()
        self.trades.append(trade.detail())
        # self.trades.append(trade)

    def detail(self):
        return {
            'id':self.id,
            'account':self.account,
            'instrument':self.instrument.upper(),
            'exchange':self.exchange,
            'asset_class':self.asset_class,
            'side':self.side,
            'type':self.type,
            'limit_price': self.limit_price,
            'avg_price': self.avg_price,
            'initial_qty': self.initial_qty,
            'filled_qty': self.filled_qty,
            'qty_unit': self.instrument.split('/')[0],
            'filled_amount': round(self.filled_amount,6),  # 成交金额
            'amount_unit': self.instrument.split('/')[1],
            'commission': round(self.commission,6),  # 手续费
            'commission_unit':self.instrument.split('/')[0] if self.side == 'buy' else self.instrument.split('/')[1],
            'status': self.status,
            'create_time': self.create_time,
            'complete_time': self.complete_time,
            'trades': self.trades
        }

    def __getitem__(self, key, default=None):
        item_value = self.__getattribute__(key) if self.__getattribute__(key) else default
        return item_value

    def __repr__(self):
        content = ', '.join(['{}: {{}}'.format(item) for item in self.__slots__[1:]]).format(
            self.id, self.account, self.instrument, self.exchange, self.asset_class, self.side,
            self.type, self.limit_price, self.avg_price, self.initial_qty, self.filled_qty,
            self.filled_amount, self.commission, self.status, self.create_time,
            self.complete_time, self.trades
        )
        return 'Order({})'.format(content)

if __name__ == '__main__':
    order1 = Order('111212', 'btc/usdt', 'binance', 'spot', 'sell', 'limit', 1200,2)
    print(order1.detail())