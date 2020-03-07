'''/*---------------------------------------------------------------------------------------------
 *  Copyright (c) VituTech. All rights reserved.
 *  Licensed under the Apache License 2.0. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/
'''
from vitu.context.context import Context
from vitu.account.account_manager import AccountManager
from vitu.trade.position.portfolio_position import PortfolioPosition

class Portfolio(object):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            self = super(Portfolio, cls).__new__(cls)
            cls._instance = self
        return cls._instance

    def __init__(self,strategy=None, start_date=None, end_date=None, commission=None,
                 frequency=None, refresh_rate=None, trigger_time=None):
        self.context = Context(self, start_date, end_date, commission, frequency, refresh_rate, trigger_time)
        self._accounts = AccountManager().create_accounts(self.context)
        self.strategy = strategy
        self._rebalance_history = dict()

        self.first_flag = True

    @property
    def accounts(self):
        return self._accounts

    @property
    def rebalance_history(self):
        return self._rebalance_history

    def get_account(self, name):
        """
        :param name: 'spot_account.okex'
        :return: account
        """
        return self.accounts[name]

    def record_history(self):
        pp_detail = dict()
        pp_total = dict()
        orders = list()
        all_total_profit = None
        last_profit_and_loss = None
        date = self.context.current_datetime()
        last_date = self.context.previous_datetime()

        for name, account in self.accounts.items():
            account = account.to_dict()
            orders.extend(account['orders'])
            account['orders'].clear()

        self.rebalance_history[date] = {
            'portfolio_position':{'detail':dict(),'total':dict()},
            'orders':dict()
        }

        for asset in self.context.asset_varieties:
            # TODO list to dict
            pp_detail[asset] = PortfolioPosition(self.context, asset, self.accounts).detail()
            # portfolio_position.append(pp_detail)
        all_total_profit = round(sum([i['total_amount'] for i in pp_detail.values()]), 4)

        # 各个持仓百分比
        for asset in self.context.asset_varieties:
            pp_detail[asset]['percentage_of_positions'] = round(pp_detail[asset]['total_amount']/all_total_profit, 4)


        if self.first_flag:
            last_profit_and_loss = 0
            for asset in self.context.asset_varieties:
                pp_detail[asset]["last_profit_and_loss"] = 0
            self.first_flag = False

        else:
            last_profit_and_loss = round((all_total_profit/self.rebalance_history[last_date]["portfolio_position"]['total']["profit"])-1, 4)
            for asset in self.context.asset_varieties:
                try:
                    profit_and_loss = round((pp_detail[asset]["total_amount"] /
                                             self.rebalance_history[last_date]["portfolio_position"]['detail'][asset]["total_amount"])-1,4)
                except:
                    profit_and_loss = 0
                pp_detail[asset]["last_profit_and_loss"] = profit_and_loss


        self.rebalance_history[date]['orders'] = orders


        pp_total = {"assets":self.context.asset_varieties,
                    "profit": all_total_profit,
                    "last_profit_and_loss": last_profit_and_loss}
        self.rebalance_history[date]["portfolio_position"]['detail'] = pp_detail
        self.rebalance_history[date]["portfolio_position"]['total'] = pp_total

        # print(self.rebalance_history)
        # logger.info('资产总价值：{}'.format(all_total_profit))






