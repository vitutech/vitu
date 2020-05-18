'''/*---------------------------------------------------------------------------------------------
 *  Copyright (c) VituTech. All rights reserved.
 *  Licensed under the Apache License 2.0. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/
'''
import math
import numpy as np

from vitu.trade.order.order import Order
from vitu.core.match_engine import match_engine
from vitu.utils.trade_utils import order_update_position
from vitu.utils.error_utils import Errors
from vitu.utils.log_utils import logger

class Account(object):
    __slots__ = [
        'context',
        'name',
        'exchange',
        'asset_class',
        'current_position',
        'history_orders',
        'orders'
    ]

    def __init__(self, context, name, exchange, asset_class, current_position):
        """
        :param name:              spot_account
        :param exchange:          binance/okex
        :param asset_class:       spot/contract
        :param current_position:  {'btc':Position,'eth':Position}
        """
        self.context = context
        self.name = name
        self.exchange = exchange
        self.asset_class = asset_class
        self.current_position = current_position     # key = 'btc'..., value = Position
        self.history_orders = dict()                    # key = id, value = Order
        self.orders = list()  # 存储今日订单

    def sell(self, symbol_exchange, price, qty):
        """
        :param symbol_exchange: "BTC/USDT.binance"
        :param price:  限价
        :param qty: 数量
        :return:
        """
        exchange = symbol_exchange.split('.')[1]
        symbol = symbol_exchange.split('.')[0]
        base_currency = symbol.split('/')[0].lower()   # btc  基础货币
        quote_currency = symbol.split('/')[1].lower()  # usdt 计价货币
        if not isinstance(price,(int,float)) or np.isnan(price):
            raise Errors.INVALID_PRICE
        if not isinstance(qty, (int, float)) or np.isnan(qty):
            raise Errors.INVALID_AMOUNT
        # 低于current_price才能卖出，高于current_price才能买入
        current_price = self.context.get_price(symbol_exchange)
        if price > current_price:
            logger.debug('限价单价格需要小于等于市场价才能卖出,卖出失败.')
            return
        if base_currency not in self.current_position.keys():
            # logger.debug('没有 {} 资产,卖出失败.'.format(base_currency))
            return

        qty = math.floor(qty*100000000)/100000000
        price = math.floor(price*100000000)/100000000
        amount = math.floor((qty*price)*100000000)/100000000

        # 判断是否有足够资金下单
        if self.current_position[base_currency].detail()['available'] < qty:
            # logger.debug('{} 不足,卖出失败.'.format(base_currency))
            return
        # 判断是否小于最下下单精度、最小下单金额
        min_order_qty = self.context.min_order[exchange][symbol.lower()]['min_order_qty']
        min_order_amount = self.context.min_order[exchange][symbol.lower()]['min_order_qty']
        if qty < min_order_qty:
            logger.debug('不足下单最小精度 {} {},卖出失败.'.format('%.6f'%min_order_qty,base_currency.upper()))
            return
        if amount < min_order_amount:
            logger.debug('不足下单最小金额 {} {},卖出失败.'.format('%.6f'%min_order_amount,quote_currency.upper()))
            return

        # 下单
        order = Order(self.context, self.name, symbol, self.exchange, self.asset_class, 'sell', 'limit', price, qty)
        order_id = order['id']
        self.history_orders[order_id] = order
        order_update_position(self.context, self.current_position, order['side'], exchange, symbol, price, qty)
        match_engine(self.current_position, self.context, order)
        if not self.orders or self.orders[0]['create_time'] == self.context.current_datetime():
            self.orders.append(order.detail())
        # logger.debug('{} 卖出成功! 价格:{} 数量:{}'.format(base_currency, price, qty))
        # return order.detail()
        return order_id

    def buy(self, symbol_exchange, price, qty):
        """
        :param symbol_exchange: "BTC/USDT.binance"
        :param price:  限价
        :param qty: 数量
        :return:
        """
        exchange = symbol_exchange.split('.')[1]
        symbol = symbol_exchange.split('.')[0]
        base_currency = symbol.split('/')[0].lower()   # btc  基础货币
        quote_currency = symbol.split('/')[1].lower()  # usdt 计价货币
        if not isinstance(price,(int,float)) or np.isnan(price):
            raise Errors.INVALID_PRICE
        if not isinstance(qty, (int, float)) or np.isnan(qty):
            raise Errors.INVALID_AMOUNT
        # 低于current_price才能卖出，高于current_price才能买入
        current_price = self.context.get_price(symbol_exchange)
        if price < current_price:
            logger.debug('限价单价格需要大于等于市场价才能买入,买入失败.')
            return
        if quote_currency not in self.current_position.keys():
            logger.debug('没有 {} 资产,买入失败.'.format(quote_currency))
            return

        qty = math.floor(qty*100000000)/100000000
        price = math.floor(price*100000000)/100000000
        amount = math.floor((qty*price)*100000000)/100000000

        # 判断是否有足够资金下单
        if self.current_position[quote_currency].detail()['available'] < amount:
            # logger.debug('{} 不足,买入失败.'.format(quote_currency))
            return
        # 判断是否小于最下下单精度、最小下单金额
        min_order_qty = self.context.min_order[exchange][symbol.lower()]['min_order_qty']
        min_order_amount = self.context.min_order[exchange][symbol.lower()]['min_order_qty']
        if qty < min_order_qty:
            logger.debug('不足下单最小精度 {} {},买入失败.'.format(min_order_qty,base_currency.upper()))
            return
        if amount < min_order_amount:
            logger.debug('不足下单最小金额 {} {},买入失败.'.format(min_order_amount,quote_currency.upper()))
            return

        # 下单
        order = Order(self.context, self.name, symbol, self.exchange, self.asset_class, 'buy', 'limit', price, qty)
        order_id = order['id']
        self.history_orders[order_id] = order
        order_update_position(self.context, self.current_position, order['side'], exchange, symbol, price, qty)
        match_engine(self.current_position, self.context, order)
        if not self.orders or self.orders[0]['create_time'] == self.context.current_datetime():
            self.orders.append(order.detail())
        # logger.debug('{} 买入成功! 价格:{} 数量:{}'.format(base_currency, price, qty))
        # return order.detail()
        return order_id

    # def sell_value(self, symbol_exchange, price, value):
    #     """
    #     :param symbol_exchange: "BTC/USDT.binance"
    #     :param price: 限价
    #     :param value: 卖出多少资产价值
    #     :return:
    #     """
    #     exchange = symbol_exchange.split('.')[1]
    #     symbol = symbol_exchange.split('.')[0]
    #     base_currency = symbol.split('/')[0].lower()  # btc  基础货币
    #     quote_currency = symbol.split('/')[1].lower()  # usdt 计价货币
    #     if not isinstance(price, (int, float)) or np.isnan(price):
    #         raise Errors.INVALID_PRICE
    #     if not isinstance(value, (int, float)) or np.isnan(value):
    #         raise Errors.INVALID_AMOUNT
    #     # 低于current_price才能卖出，高于current_price才能买入
    #     current_price = self.context.get_price(symbol_exchange)
    #     if price > current_price:
    #         logger.warning('限价单价格需要小于等于市场价才能卖出,卖出失败.')
    #         return
    #     if base_currency not in self.current_position.keys():
    #         logger.warning('没有 {} 资产,卖出失败.'.format(base_currency))
    #         return
    #
    #     qty = math.floor((value/current_price) * 100000000) / 100000000
    #     price = math.floor(price*100000000)/100000000
    #     amount = math.floor((qty*price)*100000000)/100000000
    #
    #     # 判断是否有足够资金下单
    #     if self.current_position[base_currency].detail()['available'] < qty:
    #         logger.warning('{} 不足,卖出失败.'.format(base_currency))
    #         return
    #     # 判断是否小于最下下单精度、最小下单金额
    #     min_order_qty = self.context.min_order[exchange][symbol.lower()]['min_order_qty']
    #     min_order_amount = self.context.min_order[exchange][symbol.lower()]['min_order_qty']
    #     if qty < min_order_qty:
    #         logger.warning('不足下单最小精度 {} {},卖出失败.'.format('%.6f'%min_order_qty,base_currency.upper()))
    #         return
    #     if amount < min_order_amount:
    #         logger.warning('不足下单最小金额 {} {},卖出失败.'.format('%.6f'%min_order_amount,quote_currency.upper()))
    #         return
    #
    #     # 下单
    #     order = Order(self.context, self.name, symbol, self.exchange, self.asset_class, 'sell', 'limit', price, qty)
    #     order_id = order['id']
    #     self.history_orders[order_id] = order
    #     order_update_position(self.context, self.current_position, order['side'], exchange, symbol, price, qty)
    #     match_engine(self.current_position, self.context, order)
    #     if not self.orders or self.orders[0]['create_time'] == self.context.current_datetime():
    #         self.orders.append(order.detail())
    #     logger.info('{} 卖出成功! 价格:{} 数量:{}'.format(base_currency, price, qty))
    #     return order_id
    #
    # def buy_value(self, symbol_exchange, price, value):
    #     """
    #     :param symbol_exchange: "BTC/USDT.binance"
    #     :param price:  限价
    #     :param value: 价值
    #     :return:
    #     """
    #     exchange = symbol_exchange.split('.')[1]
    #     symbol = symbol_exchange.split('.')[0]
    #     base_currency = symbol.split('/')[0].lower()   # btc  基础货币
    #     quote_currency = symbol.split('/')[1].lower()  # usdt 计价货币
    #     if not isinstance(price,(int,float)) or np.isnan(price):
    #         raise Errors.INVALID_PRICE
    #     if not isinstance(value, (int, float)) or np.isnan(value):
    #         raise Errors.INVALID_AMOUNT
    #     # 低于current_price才能卖出，高于current_price才能买入
    #     current_price = self.context.get_price(symbol_exchange)
    #     if price < current_price:
    #         logger.warning('限价单价格需要大于等于市场价才能买入,买入失败.')
    #         return
    #     if quote_currency not in self.current_position.keys():
    #         logger.warning('没有 {} 资产,买入失败.'.format(quote_currency))
    #         return
    #
    #     qty = math.floor((value/current_price) * 100000000) / 100000000
    #     price = math.floor(price*100000000)/100000000
    #     amount = math.floor((qty*price)*100000000)/100000000
    #
    #     # 判断是否有足够资金下单
    #     if self.current_position[quote_currency].detail()['available'] < amount:
    #         logger.warning('{} 不足,买入失败.'.format(quote_currency))
    #         return
    #     # 判断是否小于最下下单精度、最小下单金额
    #     min_order_qty = self.context.min_order[exchange][symbol.lower()]['min_order_qty']
    #     min_order_amount = self.context.min_order[exchange][symbol.lower()]['min_order_qty']
    #     if qty < min_order_qty:
    #         logger.warning('不足下单最小精度 {} {},买入失败.'.format(min_order_qty,base_currency.upper()))
    #         return
    #     if amount < min_order_amount:
    #         logger.warning('不足下单最小金额 {} {},买入失败.'.format(min_order_amount,quote_currency.upper()))
    #         return
    #
    #     # 下单
    #     order = Order(self.context, self.name, symbol, self.exchange, self.asset_class, 'buy', 'limit', price, qty)
    #     order_id = order['id']
    #     self.history_orders[order_id] = order
    #     order_update_position(self.context, self.current_position, order['side'], exchange, symbol, price, qty)
    #     match_engine(self.current_position, self.context, order)
    #     if not self.orders or self.orders[0]['create_time'] == self.context.current_datetime():
    #         self.orders.append(order.detail())
    #     logger.info('{} 买入成功! 价格:{} 数量:{}'.format(base_currency,price,qty))
    #     return order_id
    #
    # def sell_target_value(self, symbol_exchange, price, target_value):
    #     """
    #     :param symbol_exchange: "BTC/USDT.binance"
    #     :param price: 限价
    #     :param target_value: 卖出到剩余多少资产价值
    #     :return:
    #     """
    #     exchange = symbol_exchange.split('.')[1]
    #     symbol = symbol_exchange.split('.')[0]
    #     base_currency = symbol.split('/')[0].lower()  # btc  基础货币
    #     quote_currency = symbol.split('/')[1].lower()  # usdt 计价货币
    #     if not isinstance(price, (int, float)) or np.isnan(price):
    #         raise Errors.INVALID_PRICE
    #     if not isinstance(target_value, (int, float)) or np.isnan(target_value):
    #         raise Errors.INVALID_AMOUNT
    #     # 低于current_price才能卖出，高于current_price才能买入
    #     current_price = self.context.get_price(symbol_exchange)
    #     if price > current_price:
    #         logger.warning('限价单价格需要小于等于市场价才能卖出,卖出失败.')
    #         return
    #     if base_currency not in self.current_position.keys():
    #         logger.warning('没有 {} 资产,卖出失败.'.format(base_currency))
    #         return
    #
    #     available = self.current_position[base_currency].detail()['available']
    #
    #     value = abs(target_value-available)
    #     qty = math.floor((value / current_price) * 100000000) / 100000000
    #     print(available,target_value,qty)
    #     if qty < 0:
    #         logger.warning('{} 不足,卖出失败.'.format(base_currency))
    #         return
    #     price = math.floor(price*100000000)/100000000
    #     amount = math.floor((qty*price)*100000000)/100000000
    #
    #     # 判断是否有足够资金下单
    #     if self.current_position[base_currency].detail()['available'] < qty:
    #         logger.warning('{} 不足,卖出失败.'.format(base_currency))
    #         return
    #     # 判断是否小于最下下单精度、最小下单金额
    #     min_order_qty = self.context.min_order[exchange][symbol.lower()]['min_order_qty']
    #     min_order_amount = self.context.min_order[exchange][symbol.lower()]['min_order_qty']
    #     if qty < min_order_qty:
    #         logger.warning('不足下单最小精度 {} {},卖出失败.'.format('%.6f'%min_order_qty,base_currency.upper()))
    #         return
    #     if amount < min_order_amount:
    #         logger.warning('不足下单最小金额 {} {},卖出失败.'.format('%.6f'%min_order_amount,quote_currency.upper()))
    #         return
    #
    #     # 下单
    #     order = Order(self.context, self.name, symbol, self.exchange, self.asset_class, 'sell', 'limit', price, qty)
    #     order_id = order['id']
    #     self.history_orders[order_id] = order
    #     order_update_position(self.context, self.current_position, order['side'], exchange, symbol, price, qty)
    #     match_engine(self.current_position, self.context, order)
    #     if not self.orders or self.orders[0]['create_time'] == self.context.current_datetime():
    #         self.orders.append(order.detail())
    #     logger.info('{} 卖出成功! 价格:{} 数量:{}'.format(base_currency, price, qty))
    #     return order_id
    #
    # def buy_target_value(self, symbol_exchange, price, target_value):
    #     """
    #     :param symbol_exchange: "BTC/USDT.binance"
    #     :param price:  限价
    #     :param target_value: 买入到剩余多少价值
    #     :return:
    #     """
    #     exchange = symbol_exchange.split('.')[1]
    #     symbol = symbol_exchange.split('.')[0]
    #     base_currency = symbol.split('/')[0].lower()   # btc  基础货币
    #     quote_currency = symbol.split('/')[1].lower()  # usdt 计价货币
    #     if not isinstance(price,(int,float)) or np.isnan(price):
    #         raise Errors.INVALID_PRICE
    #     if not isinstance(target_value, (int, float)) or np.isnan(target_value):
    #         raise Errors.INVALID_AMOUNT
    #     # 低于current_price才能卖出，高于current_price才能买入
    #     current_price = self.context.get_price(symbol_exchange)
    #     if price < current_price:
    #         logger.warning('限价单价格需要大于等于市场价才能买入,买入失败.')
    #         return
    #     if quote_currency not in self.current_position.keys():
    #         logger.warning('没有 {} 资产,买入失败.'.format(quote_currency))
    #         return
    #
    #     available = self.current_position[quote_currency].detail()['available']
    #     value = math.floor((available - target_value) * 100000000) / 100000000
    #     qty = math.floor((value / current_price) * 100000000) / 100000000
    #     print(available,target_value,qty)
    #
    #     if qty < 0:
    #         logger.warning('{} 不足,买入失败.'.format(quote_currency))
    #         return
    #     price = math.floor(price*100000000)/100000000
    #     amount = math.floor((qty*price)*100000000)/100000000
    #
    #     # 判断是否有足够资金下单
    #     if self.current_position[quote_currency].detail()['available'] < amount:
    #         logger.warning('{} 不足,买入失败.'.format(quote_currency))
    #         return
    #     # 判断是否小于最下下单精度、最小下单金额
    #     min_order_qty = self.context.min_order[exchange][symbol.lower()]['min_order_qty']
    #     min_order_amount = self.context.min_order[exchange][symbol.lower()]['min_order_qty']
    #     if qty < min_order_qty:
    #         logger.warning('不足下单最小精度 {} {},买入失败.'.format(min_order_qty,base_currency.upper()))
    #         return
    #     if amount < min_order_amount:
    #         logger.warning('不足下单最小金额 {} {},买入失败.'.format(min_order_amount,quote_currency.upper()))
    #         return
    #
    #     # 下单
    #     order = Order(self.context, self.name, symbol, self.exchange, self.asset_class, 'buy', 'limit', price, qty)
    #     order_id = order['id']
    #     self.history_orders[order_id] = order
    #     order_update_position(self.context, self.current_position, order['side'], exchange, symbol, price, qty)
    #     match_engine(self.current_position, self.context, order)
    #     if not self.orders or self.orders[0]['create_time'] == self.context.current_datetime():
    #         self.orders.append(order.detail())
    #     logger.info('{} 买入成功! 价格:{} 数量:{}'.format(base_currency,price,qty))
    #     return order_id
    #
    # def sell_target_pct(self, symbol_exchange, price, target_pct):
    #     """
    #     :param symbol_exchange: "BTC/USDT.binance"
    #     :param price: 限价
    #     :param target_pct: 卖出到资产百分比的数量
    #     :return:
    #     """
    #     exchange = symbol_exchange.split('.')[1]
    #     symbol = symbol_exchange.split('.')[0]
    #     base_currency = symbol.split('/')[0].lower()  # btc  基础货币
    #     quote_currency = symbol.split('/')[1].lower()  # usdt 计价货币
    #     if not isinstance(price, (int, float)) or np.isnan(price):
    #         raise Errors.INVALID_PRICE
    #     if not isinstance(target_pct, (int, float)) or np.isnan(target_pct):
    #         raise Errors.INVALID_AMOUNT
    #     # 低于current_price才能卖出，高于current_price才能买入
    #     current_price = self.context.get_price(symbol_exchange)
    #     if price > current_price:
    #         logger.warning('限价单价格需要小于等于市场价才能卖出,卖出失败.')
    #         return
    #     if base_currency not in self.current_position.keys():
    #         logger.warning('没有 {} 资产,卖出失败.'.format(base_currency))
    #         return
    #
    #     qty = math.floor((self.current_position[base_currency].detail()['available'] * (1-target_pct)) * 100000000) / 100000000
    #     price = math.floor(price*100000000)/100000000
    #     amount = math.floor((qty*price)*100000000)/100000000
    #
    #     # 下单
    #     order = Order(self.context, self.name, symbol, self.exchange, self.asset_class, 'sell', 'limit', price, qty)
    #     order_id = order['id']
    #     self.history_orders[order_id] = order
    #     order_update_position(self.context, self.current_position, order['side'], exchange, symbol, price, qty)
    #     match_engine(self.current_position, self.context, order)
    #     if not self.orders or self.orders[0]['create_time'] == self.context.current_datetime():
    #         self.orders.append(order.detail())
    #     logger.info('{} 卖出成功! 价格:{} 数量:{}'.format(base_currency, price, qty))
    #     return order_id

    def sell_pct(self, symbol_exchange, price, pct):
        """
        :param symbol_exchange: "BTC/USDT.binance"
        :param price: 限价
        :param pct: 卖出资产百分比的数量
        :return:
        """
        exchange = symbol_exchange.split('.')[1]
        symbol = symbol_exchange.split('.')[0]
        base_currency = symbol.split('/')[0].lower()  # btc  基础货币
        # quote_currency = symbol.split('/')[1].lower()  # usdt 计价货币
        if not isinstance(price, (int, float)) or np.isnan(price):
            raise Errors.INVALID_PRICE
        if not isinstance(pct, (int, float)) or np.isnan(pct):
            raise Errors.INVALID_AMOUNT

        if base_currency not in self.current_position.keys():
            logger.debug('没有 {} 资产,卖出失败.'.format(base_currency))
            return
        base_min_qty = self.context.min_order[exchange][symbol.lower()]['min_order_qty']
        if self.current_position[base_currency].detail()['available'] < base_min_qty:
            logger.debug('{} 不足下单最小精度 {} {},卖出失败.'.format(base_currency,'%.6f'%base_min_qty,base_currency.upper()))
            return
        # 低于current_price才能卖出，高于current_price才能买入
        # current_price = self.context.get_price(symbol_exchange)
        # if price > current_price:
        #     logger.debug('限价单价格需要小于等于市场价才能卖出,卖出失败.')
        #     return

        qty = math.floor((self.current_position[base_currency].detail()['available']*pct)*1000000)/1000000
        price = math.floor(price*1000000)/1000000
        order = Order(self.context, self.name, symbol, self.exchange, self.asset_class, 'sell', 'limit', price, qty)
        order_id = order['id']
        self.history_orders[order_id] = order
        order_update_position(self.context, self.current_position, order['side'], exchange, symbol, price, qty)
        match_engine(self.current_position, self.context, order)
        if not self.orders or self.orders[0]['create_time'] == self.context.current_datetime():
            self.orders.append(order.detail())
        # logger.debug('{} 卖出成功! 价格:{} 数量:{}'.format(base_currency, price, qty))
        # return order.detail()
        return order_id

    def buy_pct(self, symbol_exchange, price, pct):
        """
        :param symbol_exchange: "BTC/USDT.binance"
        :param price:  限价
        :param pct: 买入资产百分比的数量
        :return:
        """
        exchange = symbol_exchange.split('.')[1]
        symbol = symbol_exchange.split('.')[0]
        base_currency = symbol.split('/')[0].lower()   # btc  基础货币
        quote_currency = symbol.split('/')[1].lower()  # usdt 计价货币
        if not isinstance(price,(int,float)) or np.isnan(price):
            raise Errors.INVALID_PRICE

        if quote_currency not in self.current_position.keys():
            logger.debug('没有 {} 资产,买入失败.'.format(quote_currency))
            return

        quote_min_amount = self.context.min_order[exchange][symbol.lower()]['min_order_amount']
        if self.current_position[quote_currency].detail()['available'] < quote_min_amount:
            logger.debug('{} 不足下单最小精度 {} {},买入失败.'.format(quote_currency,quote_min_amount,quote_currency.upper()))
            return
        qty = math.floor((self.current_position[quote_currency].detail()['available'] * pct)/price*1000000)/1000000
        if not isinstance(qty,(int,float)) or np.isnan(qty):
            raise Errors.INVALID_AMOUNT
        # 低于current_price才能卖出，高于current_price才能买入
        current_price = self.context.get_price(symbol_exchange)
        if price < current_price:
            logger.debug('限价单价格需要大于等于市场价才能买入,买入失败.')
            return

        price = math.floor(price*1000000)/1000000
        order = Order(self.context, self.name, symbol, self.exchange, self.asset_class, 'buy', 'limit', price, qty)
        order_id = order['id']
        self.history_orders[order_id] = order
        order_update_position(self.context, self.current_position, order['side'], exchange, symbol, price, qty)
        match_engine(self.current_position, self.context, order)
        if not self.orders or self.orders[0]['create_time'] == self.context.current_datetime():
            self.orders.append(order.detail())
        # logger.debug('{} 买入成功! 价格:{} 数量:{}'.format(base_currency,price,qty))
        # return order.detail()
        return order_id

    def get_positions(self):
        """
        :return: 获取仓位
        """
        return {asset:position.to_dict() for asset,position in self.current_position.items()}

    def get_position(self, asset):
        """
        :param asset: 币种
        :return: 获取指定asset仓位
        """
        asset = asset.lower()
        if asset not in self.current_position.keys():
            asset_position = {'asset':asset,'available':0,'frozen':0,'avg_cost_usdt':0,'avg_cost_btc':0}
            return asset_position
        else:
            return self.current_position[asset].to_dict()

    # def is_holding(self, asset):
    #     if asset.lower() in self.get_positions().keys():
    #         return True
    #     else:
    #         return False

    def get_order(self, order_id):
        """
        :param order_id: order订单号
        :return: 通过order_id找对应order详情
        """
        return self.history_orders[order_id]

    def get_orders(self, status):
        """
        :param status: 'Filled' | 'Partial_Filled' | 'Pending' | 'Cancelled' | 'Withdrawn'
        :return: 返回指定状态的所有order
        """
        return [order for order in self.history_orders.values() if order['status'] == status]

    def get_trades(self, order_id):
        """
        :param order_id: order订单号
        :return: 通过order_id找对应trades详情
        """
        return self.history_orders[order_id].trades

    @property
    def __dict__(self):
        return {key: self.__getattribute__(key) for key in self.__slots__}

    def to_dict(self):
        return self.__dict__

    def __repr__(self):
        return "Account(name: {}, exchange: {}, asset_class: {}, current_position: {}, open_orders: {})".format(
            self.name, self.exchange, self.asset_class, self.current_position, self.history_orders)

if __name__ == '__main__':
    pass