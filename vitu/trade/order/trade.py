'''/*---------------------------------------------------------------------------------------------
 *  Copyright (c) VituTech. All rights reserved.
 *  Licensed under the Apache License 2.0. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/
'''
from uuid import uuid1

class Trade(object):
    __slots__ = [
        'context',
        'id',
        'order_id',
        'side',
        'price',
        'qty',
        'create_time'
    ]
    def __init__(self, context, order_id, side, price, qty):
        self.context = context
        self.id = str(uuid1())
        self.order_id = order_id
        self.side = side
        self.price = price
        self.qty= qty
        self.create_time = context.current_datetime()

    @property
    def amount(self):
        """
        :return: 成交金额
        """
        return self.price * self.qty

    @property
    def commission(self):
        """
        :return: 成交手续费
        """
        commission = 0
        if self.side == 'buy':
            commission = self.qty * self.context.commission['taker']
        elif self.side == 'sell':
            commission = self.price * self.qty * self.context.commission['taker']
        # print(commission)
        return commission

    def detail(self):
        return {
            'id':self.id,
            'order_id':self.order_id,
            'side':self.side,
            'price':self.price,
            'qty':self.qty,
            'amount':round(self.amount,6),
            'commission':round(self.commission,6),
            'create_time':self.create_time
        }

    def __getitem__(self, key, default=None):
        item_value = self.__getattribute__(key) if self.__getattribute__(key) else default
        return item_value

    def __repr__(self):
        content = ', '.join(['{}: {{}}'.format(item) for item in self.__slots__][1:]).format(
            self.id, self.order_id, self.price, self.qty, self.amount, self.commission,
            self.create_time)
        return 'Trade({})'.format(content)