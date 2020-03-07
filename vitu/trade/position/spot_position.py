'''/*---------------------------------------------------------------------------------------------
 *  Copyright (c) VituTech. All rights reserved.
 *  Licensed under the Apache License 2.0. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/
'''
import datetime
import numpy as np

from vitu.trade.position.position import Position
from vitu.utils.date_utils import str2timestamp


class SpotPosition(Position):
    # __slots__ = [
    #     'available',
    #     'frozen',
    #     '_context'
    # ]
    def __init__(self, asset_class=None, asset=None, available=0, frozen=0, avg_cost_btc=0, avg_cost_usdt=0):
        """
        :param asset_class: 'spot'/'contract'
        :param asset: 'btc'/'eth' ...
        :param available: 可用数量
        :param frozen: 冻结数量
        :param avg_cost_btc: btc的持仓成本
        :param
        """
        super(SpotPosition, self).__init__(asset_class, asset)
        self.available = available
        self.frozen = frozen
        self.avg_cost_btc = avg_cost_btc
        self.avg_cost_usdt = avg_cost_usdt  # TDOD 哪来的None

        self._context = None

    @property
    def context(self):
        return self._context

    @context.setter
    def context(self, context):
        self._context = context

    @property
    def value(self):
        """
        :return: 持仓市值（随市场价实时变动）
        """
        if not self._context:
            return 0
        else:
            date = self._context.clock.current_date
            current_timestamp = str2timestamp(str(date.date()))  # 只关注date() time()舍掉
            # current_timestamp = datetime.datetime.timestamp(date)
            cmc_key = 'cmc-spot-' + self.asset + 'usd'
            df = self.context.cacher.data[cmc_key]
            return df.loc[(df['timestamp'] == current_timestamp)]['close'].tolist()[0]

    @property
    def total(self):
        """
        :return: 总数量
        """
        if not self.available + self.frozen:
            return 0
        else:
            return self.available + self.frozen
    @property
    def amount(self):
        """
        :return: 持仓浮动盈亏（随市场价实时变动）
        """
        if not self.value:
            return 0
        else:
            return self.total * self.value

    def order_update(self, currency_type, side, price, qty):
        """
        :param currency_type: base/quote  基础货币/计价货币
        :param side: buy/sell
        :param price: 价格
        :param qty: 数量
        """
        if side == 'buy':
            if currency_type == 'quote':
                self.available -= price * qty
                self.frozen += price * qty
        if side == 'sell':
            if currency_type == 'base':
                self.available -= qty
                self.frozen += qty

    def trade_update(self, currency_type, trade):
        """
        {
	    'id': '69327ec1-ea66-11e9-bea1-005056c00008',
	    'order_id': '69327ec0-ea66-11e9-8746-005056c00008',
	    'side': 'buy',
	    'price': 3432.88,
	    'qty': 145.65029,
	    'amount': 499999.967535,
	    'commission': 0.02913,
	    'create_time': '2018-12-10 00:00:00'
	    }
        :param currency_type: 'base'/'quote'  基础货币/计价货币
        :param trade: instance
        :param relative_currency: symol的另一个
        """
        # btc_usdt
        if trade['side'] == 'buy':
            if currency_type == 'base':
                self.available += (trade['qty'] - trade['commission'])
                # self.available += trade['qty']
            elif currency_type == 'quote':
                self.frozen -= trade['price']*trade['qty']

        if trade['side'] == 'sell':
            if currency_type == 'base':
                self.frozen -= trade['qty']
            elif currency_type == 'quote':
                self.available += (trade['price']*trade['qty']-trade['commission'])
                # self.available += trade['price']*trade['qty']

    def trade_update_cost(self, currency_type, trade, relative_currency):
        if not self.available:
            self.avg_cost_btc = 0
            self.avg_cost_usdt = 0
            return
        if trade['side'] == 'buy':
            if currency_type == 'base':
                self.avg_cost_btc = ((self.available-trade['qty']+trade['commission']) * self.avg_cost_btc +
                                     (relative_currency.avg_cost_btc * trade['amount'])) / self.available
                self.avg_cost_usdt = ((self.available-trade['qty']+trade['commission']) * self.avg_cost_usdt +
                                      (relative_currency.avg_cost_usdt * trade['amount'])) / self.available
            elif currency_type == 'quote':
                self.avg_cost_btc = self.avg_cost_btc
                self.avg_cost_usdt = self.avg_cost_usdt
        if trade['side'] == 'sell':
            if currency_type == 'base':
                self.avg_cost_btc = self.avg_cost_btc
                self.avg_cost_usdt = self.avg_cost_usdt
            elif currency_type == 'quote':
                self.avg_cost_btc = ((self.available-trade['amount']+trade['commission']) * self.avg_cost_btc +
                                     (relative_currency.avg_cost_btc * trade['qty'])) / self.available
                self.avg_cost_usdt = ((self.available-trade['amount']+trade['commission']) * self.avg_cost_usdt +
                                      (relative_currency.avg_cost_usdt * trade['qty'])) / self.available

    def detail(self):
        return {
            'asset_class':self.asset_class,
            'asset':self.asset,
            'amount':round(self.amount, 6),
            'value':round(self.value, 6),  #
            'total':round(self.total, 6),
            'available':round(self.available, 6),
            'frozen':self.frozen,

            'avg_cost_btc':self.avg_cost_btc,
            'avg_cost_usdt':self.avg_cost_usdt
        }

    def to_dict(self):
        return {
            'asset': self.asset,
            'available': round(self.available, 6),
            'frozen': self.frozen,

            'avg_cost_btc': self.avg_cost_btc,
            'avg_cost_usdt': self.avg_cost_usdt
        }

    def __repr__(self):
        return "SpotPosition(asset_class: {}, asset: {}, amount: {}, value: {}, total: {}, available: {}, frozen: {}, " \
               "avg_cost_btc: {}, avg_cost_usdt: {})".format(
            self.asset_class, self.asset, round(self.amount, 4), round(self.value, 4), round(self.total, 4),
            round(self.available, 4), self.frozen, self.avg_cost_btc, self.avg_cost_usdt)