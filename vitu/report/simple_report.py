'''/*---------------------------------------------------------------------------------------------
 *  Copyright (c) VituTech. All rights reserved.
 *  Licensed under the Apache License 2.0. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/
'''
from vitu.report.report import Report

class SimpleReport(Report):
    def __init__(self, portfolio):
        super(SimpleReport, self).__init__(portfolio)
        self.cumulative_returns = None
        self.benchmark_cumulative_returns = None
        self.returns_rate = None
        self.benchmark_returns_rate = None

        self.excess_return = None
        self.log_returns = None
        self.benchmark_log_returns = None

    def get_dates_values(self):
        """
        获取dates和values
        :return: dates和values
        """
        values = list()
        dates = list()
        benchmarks=self.benchmark 
        values.append(self.context.init_position_total)
        for date, pf in self.rebalance_history.items():
            values.append(sum([asset['total_amount'] for asset in pf['portfolio_position']['detail'].values()]))
            dates.append(date)
    
        date1=[]
        value1=[]
        for i, v in enumerate(dates):
            if v in benchmarks['timestamp'].values:
               date1.append(dates[i])
               value1.append(values[i])
        dates=date1
        values=value1
        return dates,values

    def run(self):
        self.dates,self.values = self.get_dates_values()
        self.bm_values = self.get_benchmark_values(self.dates)
        # print(self.values)

        st_returns = self.get_relative_returns(self.values)
        bm_returns = self.get_relative_returns(self.bm_values)
        # print(st_returns)

        self.cumulative_returns, self.returns_rate = self.get_cumulative_returns(st_returns)
        self.benchmark_cumulative_returns, self.benchmark_returns_rate = self.get_cumulative_returns(bm_returns)

        index = len(self.benchmark_returns_rate)
        self.excess_return = [round((self.returns_rate[-index:][i]-self.benchmark_returns_rate[i]),4)
                              for i in range(len(self.benchmark_returns_rate))]

        self.log_returns = self.get_log_returns(self.values)
        self.benchmark_log_returns = self.get_log_returns(self.bm_values)

        # 计算高级指标
        self.annualized_return = self.get_annualized_return(self.cumulative_returns)
        self.benchmark_annualized_return = self.get_annualized_return(self.benchmark_cumulative_returns)
        self.max_drawdown = self.get_max_drawdown(self.cumulative_returns)
        self.annualized_volatility = self.get_annualized_volatility(st_returns)
        rf = self.get_riskfree_rate()
        self.alpha, self.beta = self.get_CAPM(st_returns, bm_returns, rf)
        self.sharpe = self.get_sharpe(st_returns, rf)
        self.information_ratio = self.get_information_ratio(st_returns, bm_returns)
        netvalues = self.cumulative_returns
        max1 = []
        for i, v in enumerate(netvalues):
            j = max(netvalues[:i + 1])
            if j == v:
                max1.append(0)
            else:
                max1.append(1 - v / j)
        if max(max1)>0:
           a1 = max1.index(max(max1))
           a2 = netvalues.index(max(netvalues[:a1]))
           mdate1 = self.dates[a2]
           mdate2 = self.dates[a1]
           maxdown_interval = [mdate1, mdate2]
        else:
            maxdown_interval = [self.dates[0], self.dates[0]] 

        report = {
            "display_type": "strategy_overview",
            "Date": self.dates,
            "cumulative_returns": self.returns_rate,
            "netvalues": self.cumulative_returns,
            "Netvalue": self.cumulative_returns[-1],
            "benchmark_cumulative_returns": self.benchmark_returns_rate,
            "excess_return": self.excess_return,
            "log_returns": self.log_returns,
            "benchmark_log_returns": self.benchmark_log_returns,
            # 风险指标
            "annualized_return": self.annualized_return,  # 策略 年化收益
            "benchmark_annualized_return": self.benchmark_annualized_return,  # 基准 年化收益
            "cumulative_return": self.returns_rate[-1],  # 策略 累计收益
            "benchmark_cumulative_return": self.benchmark_returns_rate[-1],  # 基准 累计收益
            "alpha": self.alpha,
            "sharpe": self.sharpe,
            "information_ratio": self.information_ratio,
            "winning_ratio": '' if not self.winning_ratio else '',
            "beta": self.beta,
            "annualized_volatility": self.annualized_volatility,
            "max_drawdown": self.max_drawdown,
            "maxdown_interval": maxdown_interval
        }
        return report

