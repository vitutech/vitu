'''/*---------------------------------------------------------------------------------------------
 *  Copyright (c) VituTech. All rights reserved.
 *  Licensed under the Apache License 2.0. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/
'''
from vitu.trade.position.spot_position import SpotPosition
from vitu.trade.position.contract_position import ContractPosition
from vitu.account.account import Account
from vitu.utils.data_utils import get_btc_usdt_cost


class AccountInfo(object):
    __slots__ = [
        'name',
        'exchange',
        'account_type',
        'position_base'
    ]
    def __init__(self, name, exchange, account_type, position_base):
        self.name = name
        self.exchange = exchange
        self.account_type = account_type
        self.position_base = position_base

    def detail(self):
        return {
            'name': self.name,
            'exchange': self.exchange,
            'account_type': self.account_type,
            'position_base': self.position_base
        }

    def __getitem__(self, key, default=None):
        item_value = self.__getattribute__(key) if self.__getattribute__(key) else default
        return item_value

    def __repr__(self):
        content = ', '.join(['{}: {{}}'.format(item) for item in self.__slots__]).format(
            self.name,self.exchange,self.account_type, self.position_base)
        return 'AccountInfo({})'.format(content)



class AccountManager(object):
    __instance = None
    __has_init = False
    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def __init__(self):  # 单例模式的初始化也应该只执行一次
        if AccountManager.__has_init == False:
            self.accounts_info = []
            self._accounts_name = None  # 记录account_name
            self.asset_varieties = None
            AccountManager.__has_init = True

    def config(self, name, exchange, account_type, position_base):
        """
        :param name : spot_account:
        :param exchange : binance
        :param account_type : digital.spot/contract
        :param position_base : ({'asset': 'BTC', 'qty': 100}, {'asset': 'USDT', 'qty': 200000}))
                               ({'asset': 'XBT/USD.long', 'qty': 100, 'leverage': 100, 'insurance': 2})
        """
        self.accounts_info.append(AccountInfo(name, exchange, account_type, position_base))

    def create_accounts(self, context):
        self._accounts_name = list()
        self.asset_varieties = list()

        accounts = dict()
        for account_info in self.accounts_info:
            name = account_info['name']
            self._accounts_name.append(name)  # 添加account_name
            exchange = account_info['exchange']
            asset_class = account_info['account_type'].split('.')[1]
            current_position = dict()
            if asset_class == 'spot':
                for i in account_info['position_base']:
                    asset = i['asset'].lower()
                    # 计算初始持仓成本
                    avg_cost_btc, avg_cost_usdt = get_btc_usdt_cost(asset, context.current_datetime())
                    if asset not in self.asset_varieties:
                        self.asset_varieties.append(asset)  # 添加asset
                    available = i['qty']
                    frozen = 0
                    current_position[asset] = SpotPosition(asset_class, asset, available, frozen, avg_cost_btc, avg_cost_usdt)
            if asset_class == 'contract':
                for i in account_info['position_base']:
                    asset = i['asset'].lower().replace('.','_')
                    if asset not in self.asset_varieties:
                        self.asset_varieties.append(asset)  # 添加asset
                    available = i['qty']
                    frozen = 0
                    leverage = i['leverage']
                    insurance = i['insurance']
                    current_position[asset] = ContractPosition(asset_class, asset, available, frozen, leverage, insurance)

            accounts[name] = Account(context, name, exchange, asset_class, current_position)

        context.accounts_name = self._accounts_name
        context.asset_varieties = self.asset_varieties
        return accounts

    def __repr__(self):
        content = ', '.join(['{}: {{}}'.format(item) for item in self.__slots__]).format(self.accounts_info)
        return 'AccountManager({})'.format(content)