'''/*---------------------------------------------------------------------------------------------
 *  Copyright (c) VituTech. All rights reserved.
 *  Licensed under the Apache License 2.0. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/
'''
import datetime
import random

from vitu.report.report import Report
from vitu.account.account_manager import AccountManager
from vitu.utils.date_utils import timestamp2str,str2datetime

class CompleteReport(Report):
    def __init__(self, portfolio):
        super(CompleteReport, self).__init__(portfolio)
        self.completed_time = None
        self.benchmark_annualized_volatility = None

        self.orders = None
        self.portfolio_positions = None
        self.config = None
        self.code = None
        self.log = None

    def get_dates_values_positions_orders(self):
        """
        :return: dates、values、positions、orders
        """
        values = list()
        dates = list()
        portfolio_position = dict()
        orders = dict()
        benchmarks=self.benchmark 
        values.append(self.context.init_position_total)
        for date, pf in self.rebalance_history.items():
            values.append(sum([asset['total_amount'] for asset in pf['portfolio_position']['detail'].values()]))
            dates.append(date)
            portfolio_position[date] = pf['portfolio_position']
            orders[date] = pf['orders']
        date1=[]
        value1=[]
        portfolio_position1=dict()
        orders1 = dict()
        freq1=self.context.frequency
        if freq1 in ['d','1d','day','1day']:
            for i, v in enumerate(dates):
                if v in benchmarks['timestamp'].values:
                   date1.append(dates[i])
                   value1.append(values[i])
                   portfolio_position1[dates[i]]= portfolio_position[dates[i]]
                   orders1[dates[i]] = orders[dates[i]] 
        else:
            for i, v in enumerate(dates):
                if v in benchmarks['timestamp'].values:
                    countbar=0
                    maxnum=random.uniform(5,10)
                    date1.append(dates[i])
                    value1.append(values[i])
                    portfolio_position1[dates[i]]= portfolio_position[dates[i]]
                if  orders[dates[i]]: 
                    currentdate=str2datetime(dates[i]).replace(hour=0, minute=0, second=0, microsecond=0)
                    if bool(orders1):
                       if (str(currentdate)) not in orders1.keys():
                          orders1[str(currentdate)]=[]
                       tempdate=list(orders1.keys())[-1]
                       orderdate=str2datetime(tempdate).replace(hour=0, minute=0, second=0, microsecond=0)
                       if currentdate==orderdate:
                          countbar+=1
                          if countbar<=maxnum: 
                            orders1[str(currentdate)].append(orders[dates[i]][0])
                       else: 
                            orders1[str(currentdate)].append(orders[dates[i]][0])
                    else:
                        currentdate=str2datetime(dates[i]).replace(hour=0, minute=0, second=0, microsecond=0) 
                        orders1[str(currentdate)]=[]
                        orders1[str(currentdate)].append(orders[dates[i]][0])
        dates=date1
        values=value1
        portfolio_position=portfolio_position1
        orders=orders1
        return dates,values,portfolio_position,orders

    def get_cross_months(self, start_date, end_date):
        """
        :param start_date: "2019-05-31"
        :param end_date: "2019-08-03"
        :return: months 两个日期间跨几个月
        """
        start_year = datetime.datetime.strptime(start_date[:10], "%Y-%m-%d").year
        end_year = datetime.datetime.strptime(end_date[:10], "%Y-%m-%d").year
        start_month = datetime.datetime.strptime(start_date[:10], "%Y-%m-%d").month
        end_month = datetime.datetime.strptime(end_date[:10], "%Y-%m-%d").month
        months = (end_year - start_year) * 12 + (end_month - start_month + 1)
        return months

    def risk_metrics(self, st_returns, bm_returns):
        """
        :param st_returns: 策略相对收益率 列表
        :param bm_returns: 基准相对收益率 列表
        :return: 计算指标（核心）
        """
        cumulative_returns = self.get_cumulative_returns(st_returns)[0]
        benchmark_cumulative_returns = self.get_cumulative_returns(bm_returns)[0]

        annualized_return = self.get_annualized_return(cumulative_returns)
        benchmark_annualized_return = self.get_annualized_return(benchmark_cumulative_returns)
        max_drawdown = self.get_max_drawdown(cumulative_returns)

        annualized_volatility = self.get_annualized_volatility(st_returns)
        benchmark_annualized_volatility = self.get_annualized_volatility(bm_returns)
        rf = self.get_riskfree_rate()
        alpha, beta = self.get_CAPM(st_returns, bm_returns, rf)
        sharpe = self.get_sharpe(st_returns, rf)
        information_ratio = self.get_information_ratio(st_returns, bm_returns)

        report = {
            "annualized_return": annualized_return,
            "benchmark_annualized_return": benchmark_annualized_return,
            "alpha": alpha,
            "sharpe": sharpe,
            "information_ratio": information_ratio,
            "winning_ratio": None,
            "beta": beta,
            "annualized_volatility": annualized_volatility,
            "benchmark_annualized_volatility": benchmark_annualized_volatility,
            "max_drawdown": max_drawdown
        }
        return report

    def get_monthly(self, dates, number):
        """
        :param dates: 日期
        :param number: 几个月
        :return: 获取n个月字符串 列表
        """
        start_year = datetime.datetime.strptime(dates[0], "%Y-%m-%d %H:%M:%S").year
        start_month = datetime.datetime.strptime(dates[0], "%Y-%m-%d %H:%M:%S").month
        end_year = datetime.datetime.strptime(dates[-1], "%Y-%m-%d %H:%M:%S").year
        end_month = datetime.datetime.strptime(dates[-1], "%Y-%m-%d %H:%M:%S").month
        start_month += (number-1)
        if start_month > 12:
            start_month = start_month -12
            start_year += 1

        monthly = []
        while True:
            if start_year < end_year:
                monthly.append([start_year, start_month])
                start_month += 1
                if start_month > 12:
                    start_month = 1
                    start_year += 1
            if start_year == end_year:
                monthly.append([start_year, start_month])
                start_month += 1
                if start_month > end_month:
                    break
        return monthly

    def get_indexs(self, dates):
        """
        :param dates: 日期
        :return: 按1个月划分索引切点 列表
        """
        one_monthly = self.get_monthly(dates, 1)
        indexs = list()
        for monthly_index, monthly in enumerate(one_monthly):
            for date_index, date in enumerate(dates):
                if monthly_index == 0 and date_index == len(dates) - 1:
                    indexs.append(date_index)
                day = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
                if day.year == monthly[0] and day.month == monthly[1]:
                    indexs.append(date_index)
                    break  # 匹配到，就跳出内循环
        indexs.append(len(dates) - 1)  # 增加最后索引
        indexs.sort()
        return indexs

    def calculate_monthly_metrics(self, month, dates, st_returns, bm_returns):
        """
        :param month: 几个月
        :param dates: 日期
        :param st_returns: 策略相对收益率 列表
        :param bm_returns: 基准相对收益率 列表
        :return: 计算几个月的指标
        """
        monthly = self.get_monthly(dates,month)
        indexs = self.get_indexs(dates)
        report = dict()
        for num in range(len(monthly)):
            date_format = str()
            if len(str(monthly[num][1])) == 1:
                date_format = "{}-0{}".format(monthly[num][0],monthly[num][1])
            if len(str(monthly[num][1])) == 2:
                date_format = "{}-{}".format(monthly[num][0],monthly[num][1])
            left = indexs[num]
            right = indexs[num+month]
            if left>0 :
               left-=1
               right-=1
               
            if right == left:
                if right==len(st_returns):
                    left-=2
                    right-=1
                else:
                    left-=1 
            report[date_format] = self.risk_metrics(st_returns[left:right], bm_returns[left:right])

        new_report = {
            "annualized_return": {},
            "benchmark_annualized_return": {},
            "alpha": {},
            "sharpe": {},
            "information_ratio": {},
            "winning_ratio": {},
            "beta": {},
            "annualized_volatility": {},
            "benchmark_annualized_volatility": {},
            "max_drawdown": {},
        }
        for date, metrics in report.items():
            new_report["annualized_return"][date] = metrics["annualized_return"]
            new_report["benchmark_annualized_return"][date] = metrics["benchmark_annualized_return"]
            new_report["alpha"][date] = metrics["alpha"]
            new_report["sharpe"][date] = metrics["sharpe"]
            new_report["information_ratio"][date] = metrics["alpha"]
            new_report["winning_ratio"][date] = metrics["sharpe"]
            new_report["beta"][date] = metrics["beta"]
            new_report["annualized_volatility"][date] = metrics["annualized_volatility"]
            new_report["benchmark_annualized_volatility"][date] = metrics["benchmark_annualized_volatility"]
            new_report["max_drawdown"][date] = metrics["max_drawdown"]
        return new_report

    def run(self):
        import time
        # start1 = time.time()

        self.dates,self.values,self.portfolio_positions,self.orders = self.get_dates_values_positions_orders()
        self.bm_values = self.get_benchmark_values(self.dates)
        st_returns = self.get_relative_returns(self.values)
        bm_returns = self.get_relative_returns(self.bm_values)

        report = dict()
        report["last_one_month"] = self.calculate_monthly_metrics(1, self.dates, st_returns, bm_returns)
        cross_months = self.get_cross_months(self.context.portfolio.strategy.start, self.context.portfolio.strategy.end)
        if cross_months >= 3:
            report["last_three_month"] = self.calculate_monthly_metrics(3, self.dates, st_returns, bm_returns)
        if cross_months >= 6:
            report["last_six_month"] = self.calculate_monthly_metrics(6, self.dates, st_returns, bm_returns)
        if cross_months >= 12:
            report["last_twelve_month"] = self.calculate_monthly_metrics(12, self.dates, st_returns, bm_returns)

        new_report = {
            "display_type": "strategy_detail",
            # 风险指标
            "returns":{},
            "alpha": {},
            "sharpe": {},
            "information_ratio": {},
            "winning_ratio": {},
            "beta": {},
            "volatility":{},
            "max_drawdown": {},
        }
        for date, metrics in report.items():
            new_report["returns"][date] = {'annualized_return': metrics['annualized_return'],
                          'benchmark_annualized_return': metrics['benchmark_annualized_return']}
            excess_return = {}
            for key, value in metrics['annualized_return'].items():
                excess_return[key] = round((value - metrics['benchmark_annualized_return'][key]), 4)
            new_report["returns"][date]['excess_return'] = excess_return

            new_report["alpha"][date] = {"alpha": metrics["alpha"]}
            new_report["sharpe"][date] = {"sharpe": metrics["sharpe"]}
            new_report["information_ratio"][date] = {"information_ratio": metrics["information_ratio"]}
            new_report["beta"][date] = {"beta": metrics["beta"]}

            new_report["volatility"][date] = {'annualized_volatility': metrics['annualized_volatility'],
                          'benchmark_annualized_volatility': metrics['benchmark_annualized_volatility']}
            excess_volatility = {}
            for key, value in metrics['annualized_volatility'].items():
                excess_volatility[key] = round((value - metrics['benchmark_annualized_volatility'][key]), 4)
            new_report["volatility"][date]['excess_volatility'] = excess_volatility

            new_report["max_drawdown"][date] = {"max_drawdown": metrics["max_drawdown"]}

        orders_list = []
        for _,orders in self.orders.items():
            orders_list.extend(orders)

        filled_price = []
        filled_qty = []
        filled_amount = []
        commission = []
        if not orders_list:
            filled_price = [0]
            filled_qty = [0]
            filled_amount = [0]
            commission = [0]
        else:
            for order in orders_list:
                filled_price.append(order['limit_price'])
                filled_qty.append(order['filled_qty'])
                filled_amount.append(order['filled_amount'])
                commission.append(order['commission'])

        positions_list = []
        for _,positions in self.portfolio_positions.items():
            positions_list.extend(positions['detail'].values())
        total_qty = []
        total_amount = []
        value = []
        last_profit_and_loss = []
        percentage_of_positions = []
        avg_cost_btc = []
        avg_cost_usdt = []
        for position in positions_list:
            total_qty.append(position['total_qty'])
            total_amount.append(position['total_amount'])
            value.append(position['value'])
            last_profit_and_loss.append(position['last_profit_and_loss'])
            percentage_of_positions.append(position['percentage_of_positions'])
            avg_cost_btc.append(position['avg_cost_btc'])
            avg_cost_usdt.append(position['avg_cost_usdt'])

        new_report["info"] = {"orders":{"account_name":self.context.accounts_name,
                                        "universe": self.context.portfolio.strategy.universe,
                                        "filled_price":{'max':max(filled_price),'min':min(filled_price)},
                                        "filled_qty":{'max':max(filled_qty),'min':min(filled_qty)},
                                        "filled_amount":{'max':max(filled_amount),'min':min(filled_amount)},
                                        "commission":{'max':max(commission),'min':min(commission)}
                                        },
                              "positions":{"cryptos":self.context.asset_varieties,
                                           "total_qty":{'max':max(total_qty),'min':min(total_qty)},
                                           "total_amount": {'max':max(total_amount),'min':min(total_amount)},
                                           "value":{'max':max(value),'min':min(value)},
                                           "last_profit_and_loss":{'max':max(last_profit_and_loss),'min':min(last_profit_and_loss)},
                                           "percentage_of_positions":{'max':max(percentage_of_positions),'min':min(percentage_of_positions)},
                                           "avg_cost_btc":{'max':max(avg_cost_btc),'min':min(avg_cost_btc)},
                                           "avg_cost_usdt": {'max': max(avg_cost_usdt),'min': min(avg_cost_usdt)},
                                           }}

        new_report["completed_time"] = self.context.completed_time

        # 过滤当天为空的订单
        orders = {date:order for date,order in self.orders.items() if order}
        new_report["orders"] = orders

        new_report["portfolio_positions"] = self.portfolio_positions

        # time.sleep(0.2)
        run_end = self.context.clock.run_end if self.context.clock.run_end else time.time()
        config = {"backtest_interval":{"start":self.context.portfolio.strategy.start,
                                       "end":self.context.portfolio.strategy.end},
                  "account_name":[account.detail() for account in AccountManager().accounts_info],
                  "freq":self.context.portfolio.strategy.frequency,
                  "run_time":{"start":timestamp2str(self.context.clock.run_start),
                              "end":timestamp2str(run_end)}}
        new_report["config"] = config

        # for name in account_manager.accounts_name:
        #     name_position = "{}_position".format(name)
        #     new_report[name_position] = [{date:pf[name_position]}for date, pf in self.rebalance_history.items()]

        # start22 = time.time()
        for name in self.context.accounts_name:
            name_position = "{}_position".format(name)
            new_report[name_position] = dict()
            account_first = True

            for date, portfolio in self.rebalance_history.items():
                if date in self.benchmark['timestamp'].values:
                    last_date = str(datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S') - datetime.timedelta(days=1))
                    asset_value = dict()
                    # 计算每个account的各个asset的last_profit_and_loss
                    for asset in portfolio["portfolio_position"]['detail'].values():
                        if name in asset["consist_of"].keys():
                            asset_value[asset["asset"]] = asset["consist_of"][name]
                            # if account_first:
                            #     last_profit_and_loss = (asset["consist_of"][name]['amount'] / self.context.init_portfolio_position[asset["asset"]]["consist_of"][name]['amount']) - 1
                            #     asset_value[asset["asset"]]['last_profit_and_loss'] = round(last_profit_and_loss, 4)
                            if account_first:
                                asset_value[asset["asset"]]['last_profit_and_loss'] = 0
                            else:
                                try:
                                    last_profit_and_loss = (asset["consist_of"][name]['amount'] / self.rebalance_history[last_date]["portfolio_position"]['detail'][asset["asset"]]["consist_of"][name]['amount']) - 1
                                    asset_value[asset["asset"]]['last_profit_and_loss'] = round(last_profit_and_loss, 4)
                                except:
                                    asset_value[asset["asset"]]['last_profit_and_loss'] = 0


                            # 买入数量、买入均价、卖出数量、卖出均价
                            # for d, orders in self.orders.items():
                            #     if date == d:
                            #         buy_avg_price = []
                            #         buy_qty = []
                            #         sell_avg_price = []
                            #         sell_qty = []
                            #         for order in orders:
                            #             if order['instrument'].split('/')[0].split('/')[0] == asset["asset"]:
                            #                 if order['side'] == 'buy':
                            #                     buy_avg_price.append(order['avg_price'])
                            #                     buy_qty.append(order['filled_qty'])
                            #                 elif order['side'] == 'buy':
                            #                     sell_avg_price.append(order['avg_price'])
                            #                     sell_qty.append(order['filled_qty'])
                            #         buy = {'buy_avg_price': np.mean(buy_avg_price) if buy_avg_price else 0,
                            #                'buy_qty': np.sum(buy_qty) if buy_qty else 0}
                            #         sell = {'sell_avg_price': np.mean(sell_avg_price) if sell_avg_price else 0,
                            #                 'sell_qty': np.sum(sell_qty) if sell_qty else 0}
                            #         asset_value[asset["asset"]]['buy'] = buy
                            #         asset_value[asset["asset"]]['sell'] = sell

                    account_first = False
                    position = {"detail": dict(), "total": dict()}
                    position['detail'] = asset_value
                    new_report[name_position][date] = position

                    # 计算amount
                    amount = 0
                    for asset,value in asset_value.items():
                        amount += value['amount']
                    total = {"assets":list(asset_value.keys()),
                            "amount":round(amount,4)}
                    new_report[name_position][date]['total'] = total

                    # 计算所占百分比
                    for asset, value in asset_value.items():
                        value['percentage_of_positions'] = round(value['amount']/new_report[name_position][date]['total']['amount'], 4)

                # 计算每个account的总的last_profit_and_loss
                date_first = True
                for date,value in new_report[name_position].items():
                    last_date = str(datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S') - datetime.timedelta(days=1))
                    if date_first:
                        last_profit_and_loss = (value['total']['amount']/self.context.init_total_account_position[name_position])-1
                    else:
                        last_profit_and_loss = (value['total']['amount']/new_report[name_position][last_date]['total'])-1
                    value['total']['last_profit_and_loss'] = round(last_profit_and_loss, 4)

            # for name in self.context.accounts_name:
            #     name_position = "{}_position".format(name)
            #     new_report[name_position] = dict()
            #     for date, pf in self.rebalance_history.items():
            #         asset_value = dict()
            #         assets = list(pf["portfolio_position"].values())
            #         assets.pop()
            #         for asset in assets:
            #             if name in asset["consist_of"].keys():
            #                 asset_value[asset["asset"]] = asset["consist_of"][name]
            #         new_report[name_position][date] = asset_value
            # print("【name_position耗时】：{}".format(time.time()-start22))





        # print("【complete_report耗时】：{} s".format(str(time.time() - start1)[:5]))

        AccountManager().accounts_info = []
        return new_report



if __name__ == "__main__":
    pass





