'''/*---------------------------------------------------------------------------------------------
 *  Copyright (c) VituTech. All rights reserved.
 *  Licensed under the Apache License 2.0. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/
'''
from vitu.trade.position.position import Position

class ContractPosition(Position):
    __slots__ = [
        'available_balance',
        'side',
        'available_qty',
        'frozen_qty',
        'insurance',
        'leverage',
        'realised_pnl'
    ]
    def __init__(self, available_balance=None, asset_class=None, asset=None, side=None, available_qty=None,
                 frozen_qty=None,insurance=None, leverage=None, realised_pnl=None):
        """
        :param asset_class: 'spot'/'contract'
        :param asset: 'xbtT19' 合约标的
        :param available_balance: 账户余额
        :param side: long/short
        :param available_qty: 可用合约数量
        :param frozen_qty: 冻结合约数量
        :param insurance: 保证金
        :param leverage: 杠杆倍数
        :param realised_profit_and_lost: 已实现盈亏
        """
        super(ContractPosition, self).__init__(asset_class, asset)
        self.available_balance = available_balance
        self.side = side
        self.available_qty = available_qty
        self.frozen_qty = frozen_qty
        self.insurance = insurance
        self.leverage = leverage
        self.realised_pnl = realised_pnl

    @property
    def total_qty(self):
        return self.available_qty + self.frozen_qty

    def detail(self):
        return {
            'asset_class':self.asset_class,
            'asset':self.asset,
            'available_balance':self.available_balance,
            'side':self.side,
            'total_qty':self.total_qty,
            'available_qty':self.available_qty,
            'frozen_qty':self.frozen_qty,
            'insurance':self.insurance,
            'leverage': self.leverage,
            'realised_pnl': self.realised_pnl
        }

    def __repr__(self):
        return "FuturePosition(asset_class: {}, asset: {}, available_balance: {}, side: {}, available_qty: {}, " \
               "frozen_qty: {}, insurance: {}, leverage: {}, realised_pnl: {})".format(
            self.asset_class, self.asset, self.available_balance, self.side, self.available_qty, self.frozen_qty,
            self.insurance, self.leverage, self.realised_pnl)
