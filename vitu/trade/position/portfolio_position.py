'''/*---------------------------------------------------------------------------------------------
 *  Copyright (c) VituTech. All rights reserved.
 *  Licensed under the Apache License 2.0. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/
'''
class PortfolioPosition():
    def __init__(self, context=None, asset=None, accounts=None):
        self.context = context
        self.asset = asset
        self.accounts = accounts

        self.asset_class = None
        self.total_amount = 0
        self.value = 0
        self.total_qty = 0

        self.avg_cost_btc_total = 0
        self.avg_cost_usdt_total = 0
        self.avg_cost_btc = 0
        self.avg_cost_usdt = 0

        self.consis_of = dict()


    def detail(self):
        for account in self.accounts.values():
            account = account.to_dict()
            if self.asset in account['current_position'].keys():
                self.asset_class = account['asset_class']
                self.total_amount += account['current_position'][self.asset].detail()['amount']
                self.value = account['current_position'][self.asset].detail()['value']
                self.total_qty += account['current_position'][self.asset].detail()['total']
                self.avg_cost_btc_total += account['current_position'][self.asset].detail()['avg_cost_btc']
                self.avg_cost_usdt_total += account['current_position'][self.asset].detail()['avg_cost_usdt']
                self.consis_of[account['name']] = account['current_position'][self.asset].detail()
        self.avg_cost_btc = self.avg_cost_btc_total/len(self.consis_of)
        self.avg_cost_usdt = self.avg_cost_usdt_total/len(self.consis_of)

        return {
            'asset':self.asset,
            'asset_class' : self.asset_class,
            'total_amount': round(self.total_amount, 4),
            'value': round(self.value,4),
            'total_qty': round(self.total_qty, 4),
            'avg_cost_btc': self.avg_cost_btc,
            'avg_cost_usdt': self.avg_cost_usdt,
            'rebalance_time':self.context.current_datetime(),
            'consist_of': self.consis_of  #  key = accountName, value = position
        }

    def __getitem__(self, key, default=None):
        item_value = self.__getattribute__(key) if self.__getattribute__(key) else default
        return item_value

if __name__ == '__main__':
    pass
