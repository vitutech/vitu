'''/*---------------------------------------------------------------------------------------------
 *  Copyright (c) VituTech. All rights reserved.
 *  Licensed under the Apache License 2.0. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/
'''
from vitu.account.account import Account

class ContractAccount(Account):
    def __init__(self, name, exchange, asset_class, current_position):
        """
        {"account_id": 1,
        "exchange": 'huobi',
        "api_key": 'spot_account',
        "market": 'spot',
        "position": ({'name': 'XBT/USD.long', 'qty': 100, 'leverage': 100, 'insurance': 2})}
        """
        super(ContractAccount,self).__init__(name, exchange, asset_class, current_position)
