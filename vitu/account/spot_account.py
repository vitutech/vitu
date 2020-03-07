'''/*---------------------------------------------------------------------------------------------
 *  Copyright (c) VituTech. All rights reserved.
 *  Licensed under the Apache License 2.0. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/
'''
from vitu.account.account import Account

class SpotAccount(Account):
    def __init__(self, name, exchange, asset_class, current_position):
        """
        {"account_id": 1,
        "exchange": 'huobi',
        "api_key": 'spot_account',
        "market": 'spot',
        "position": ({'name': 'BTC', 'qty': 100}, {'name': 'USDT', 'qty': 200000})}
        """
        super(SpotAccount,self).__init__(name, exchange, asset_class, current_position)