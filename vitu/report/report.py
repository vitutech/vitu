'''/*---------------------------------------------------------------------------------------------
 *  Copyright (c) VituTech. All rights reserved.
 *  Licensed under the Apache License 2.0. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/
'''
import copy
import datetime
import math

import numpy as np
from vitu.utils.date_utils import str2datetime, str2timestamp, get_dates_length

class Report(object):
    def __init__(self, portfolio=None):
        self.rebalance_history = portfolio.rebalance_history
        self.index_key = 'chainext-index-' + portfolio.strategy.benchmark
        
        self.context = portfolio.context
        self.refresh_rate = portfolio.strategy.refresh_rate

        self.dates = [date for date in self.rebalance_history.keys()]
        benchmark1= portfolio.context.cacher.data[self.index_key]
        self.benchmark=benchmark1[(benchmark1['timestamp']>=self.dates[0])&(benchmark1['timestamp']<=self.dates[-1])]
        self.dates_length = get_dates_length(self.dates[0], self.dates[-1])  # 计算年化时，算date_length,只算日长度
        # self.dates = None
        self.values = None
        self.bm_values = None

        self.annualized_return = None
        self.benchmark_annualized_return = None
        self.alpha = None
        self.sharpe = None
        self.information_ratio = None
        self.winning_ratio = None
        self.beta = None
        self.annualized_volatility = None
        self.max_drawdown = None

    def get_benchmark_values(self, dates):
        # 不管几点，要对应整点的的日级数据
        # start = str_to_timestamp(str((str_to_datetime(dates[0]) - datetime.timedelta(days=self.refresh_rate)).date()))
        if self.context.frequency in ['d','1d','day','1day']:
            start = str((str2datetime(dates[0]) - datetime.timedelta(days=self.refresh_rate)))  
            end = str((str2datetime(dates[-1])))
            bm_values = self.benchmark.loc[(self.benchmark["timestamp"] >= start) & (self.benchmark["timestamp"]<= end)]
            bm_values = bm_values.loc[bm_values.index[::self.refresh_rate]]['close'].tolist()
        else:
            start = str((str2datetime(dates[0]) - datetime.timedelta(days=1)))  #benchmarkvalue只取对应基准的日价值，所以每日值都取
            end = str((str2datetime(dates[-1])))
            bm_values = self.benchmark.loc[(self.benchmark["timestamp"] >= start) & (self.benchmark["timestamp"]<= end)]
            bm_values = bm_values['close'].tolist()
        return bm_values

    def get_relative_returns(self, values):
        """
        根据 总净值 计算 相对收益率
        :param values: 总净值 列表
        :return: 相对收益率 列表
        """
        returns = list()
        for num, value in enumerate(values[1:]):
            if not values[num] or not value or np.isnan(value / values[num]):
                returns.append(0)
                continue
            returns.append(round((value / values[num] - 1),4))
        return returns

    def get_log_returns(self, values):
        """
        :param values: 总净值 列表
        :return: 对数收益率 列表
        """
        # print(values)
        log_returns = []
        for i in range(len(values)-1):
            try:
                num = round(math.log(values[i + 1] / values[i],math.e), 4)
            except:
                num = 0
            log_returns.append(num)
        return log_returns
        # return [round(math.log(values[i + 1] / values[i],math.e), 4) for i in range(len(values) - 1)]

    def get_returns(self, values):
        """
        :param values: 总净值 列表
        :return: 累计收益率 列表
        """
        # print(values)
        return [round(values[i + 1] / values[i]-1, 4) for i in range(len(values) - 1)]

    # -----------------------------------------------
    def get_cumulative_returns(self, returns):
        """
        根据 相对收益率 计算 绝对收益率、收益率
        :param returns: 相对收益率 列表
        :return: 绝对收益率、收益率 列表
        """
        c_returns = copy.deepcopy(returns)
        try:
            c_returns[0] += 1
        except:
            return list()
        for i, r in enumerate(c_returns[1:]):
            c_returns[i + 1] = round(((1 + r) * c_returns[i]),4)
            if np.isnan(c_returns[i + 1]) or c_returns[i + 1] < 0:
                c_returns[i + 1] = 0
        c_returns_rate = [round(i-1,4) for i in c_returns]
        return c_returns,c_returns_rate

    def get_annualized_return(self, c_returns):
        """
        根据 累计收益率 计算 年化收益率
        :param c_returns: 累计收益率 列表
        :return: 年化收益率
        """
        return round((c_returns[-1] ** (365. / self.dates_length) - 1),4)
        # return round((c_returns[-1] ** (365. / len(c_returns)) - 1),4)


    def get_max_drawdown(self, c_returns):
        """
        根据 累计收益率 计算 最大回撤
        :param c_returns: 累计收益率 列表
        :return: 最大回撤
        """
        drawdown = []
        for i, v in enumerate(c_returns):
            j = max(c_returns[:i + 1])
            if j == 0:
                drawdown.append(0)
            else:
                drawdown.append(1 - v / j)
        # drawdown = [1 - v / max(c_returns[:i + 1]) for i, v in enumerate(c_returns)]
        return round((max(drawdown)),4)

    def get_riskfree_rate(self):
        """
        获得无风险利率
        """
        return 0.01

    def get_annualized_volatility(self, returns):
        """
        根据 相对收益率 计算 收益波动率 = 收益率的(年化)标准差
        :param returns: 相对收益率 列表
        :return: 收益波动率
        """
        # annualized_volatility = np.sqrt((365/(len(returns)-1))*sum([(i - np.mean(returns)) ** 2 for i in returns]))
        std_i = []
        for i in returns:
            std_i.append((i - np.mean(returns)) ** 2)
        annualized_volatility = np.sqrt((365/(len(returns)))*sum(std_i))
        # annualized_volatility = np.sqrt((365/(len(returns)))*sum([(i - np.mean(returns)) ** 2 for i in returns]))
        return round(annualized_volatility, 4)

    def get_beta(self, st_returns, bm_returns):
        """
        根据 策略累计收益率 基准累计收益率 计算 beta
        :param st_returns: 策略累计收益率 列表
        :param bm_returns: 基准累计收益率 列表
        :param rf: 无风险利率
        :return: beta：反映策略表现对大盘变化的敏感性，即策略与大盘的相关性
        """
        d = len(st_returns)
        if d == 1:
            # return None, None
            return 0, 0
        mean_st = sum(st_returns) / d
        mean_bm = sum(bm_returns) / d
        mul = [st_returns[i] * bm_returns[i] for i in range(d)]
        cov = sum(mul) / d - mean_st * mean_bm
        var_bm = np.std(bm_returns) ** 2
        if var_bm == 0:
            return 0
        beta = cov / var_bm
        return round(beta,4)

    def get_alpha(self, st_returns, bm_returns, rf):
        """
        根据 策略累计收益率 基准累计收益率 无风险利率 计算 alpha
        :param st_returns: 策略累计收益率 列表
        :param bm_returns: 基准累计收益率 列表
        :param rf: 无风险利率
        :return: alpha：阿尔法是超额收益，它与市场波动无关
        """
        d = len(st_returns)
        if d == 1:
            # return None, None
            return 0, 0
        mu_st = sum(st_returns) / d
        mu_bm = sum(bm_returns) / d
        mul = [st_returns[i] * bm_returns[i] for i in range(d)]
        cov = sum(mul) / d - mu_st * mu_bm
        var_bm = np.std(bm_returns) ** 2
        if np.isnan(cov / var_bm):
            # return None, None
            return 0, 0
        beta = cov / var_bm
        if beta in [-np.inf, np.inf] or np.isnan(beta):
            return 0, 0
            # return None, None
        cummulative_st = self.get_cumulative_returns(st_returns)[0]
        annulized_st = self.get_annualized_return(cummulative_st)
        cummulative_bm = self.get_cumulative_returns(bm_returns)[0]
        annulized_bm = self.get_annualized_return(cummulative_bm)
        alpha = (annulized_st - rf) - beta * (annulized_bm - rf)
        return round(alpha,4)

    def get_CAPM(self, st_returns, bm_returns, rf):
        """
        根据 策略累计收益率 基准累计收益率 无风险利率 计算 beta和alpha
        :param st_returns: 策略累计收益率 列表
        :param bm_returns: 基准累计收益率 列表
        :param rf: 无风险利率
        :return: beta和alpha
        """
        d = len(st_returns)
        if d == 1:
            # return None, None
            return 0, 0
        mu_st = sum(st_returns) / d
        mu_bm = sum(bm_returns) / d
        mul = [st_returns[i] * bm_returns[i] for i in range(d)]

        cov = sum(mul) / d - mu_st * mu_bm
        var_bm = np.std(bm_returns) ** 2
        if not var_bm:
            # return None,None
            return 0, 0
        beta = cov / var_bm
        if beta in [-np.inf, np.inf] or np.isnan(beta):
            # return None, None
            return 0, 0
        cummulative_st = self.get_cumulative_returns(st_returns)[0]
        annulized_st = self.get_annualized_return(cummulative_st)
        cummulative_bm = self.get_cumulative_returns(bm_returns)[0]
        annulized_bm = self.get_annualized_return(cummulative_bm)

        alpha = (annulized_st - rf) - beta * (annulized_bm - rf)
        return round(alpha,4), round(beta,4)

    def get_sharpe(self, st_returns, rf):
        """
        根据 策略累计收益率 无风险利率 计算 sharpe
        :param st_returns: 策略累计收益率 列表
        :param rf: 无风险利率
        :return: sharpe：单位总风险下所能获得的超额收益，即每承受一单位总风险，会产生多少的超额收益
        """
        cummulative_st = self.get_cumulative_returns(st_returns)[0]
        annulized_st = self.get_annualized_return(cummulative_st)
        volatility_st = self.get_annualized_volatility(st_returns)
        if volatility_st == 0:
            return 0
        sharpe = (annulized_st - rf) / volatility_st
        return round(sharpe,4)

    def get_information_ratio(self, st_returns, bm_returns):
        """
        根据 策略累计收益率 基准累计收益率 计算 信息比率IR
        :param st_returns: 策略累计收益率 列表
        :param bm_returns: 基准累计收益率 列表
        :return: IR：单位超额风险下的超额收益。它用于衡量单位超额风险带来的超额收益。信息比率越大，说明该策略单位跟踪误差所获得的超额收益越高
        """
        d = len(st_returns)
        if d == 1:
            return 0
        diff = [st_returns[i] - bm_returns[i] for i in range(d)]
        cummulative_st = self.get_cumulative_returns(st_returns)[0]
        annulized_st = self.get_annualized_return(cummulative_st)
        cummulative_bm = self.get_cumulative_returns(bm_returns)[0]
        annulized_bm = self.get_annualized_return(cummulative_bm)
        annulized_std = (np.var(diff, ddof=1) * 365) ** 0.5
        if annulized_std == 0:
            return 0
        IR = (annulized_st - annulized_bm) / annulized_std
        if IR in [np.inf, -np.inf] or np.isnan(IR):
            return 0
        return round(IR,4)

    def __getitem__(self, key, default=None):
        item_value = self.__getattribute__(key) if self.__getattribute__(key) else default
        return item_value

if __name__ == '__main__':
    print(round(((1.26 ** (365. / 690)) - 1), 4))
    print(round(((1.3 ** (365. / 720)) - 1), 4))