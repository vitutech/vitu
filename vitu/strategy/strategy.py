import traceback
import pandas as pd
import datetime
import time
import matplotlib.pyplot as plt
import xlwt
import os 

from vitu.account.account_manager import AccountManager
from vitu.trade.portfoilo.portfolio import Portfolio
from vitu.trade.position.portfolio_position import PortfolioPosition
from vitu.report.simple_report import SimpleReport
from vitu.report.complete_report import CompleteReport
from vitu.utils.date_utils import str2timestamp, get_total_dates, str2datetime,get_day_dates
from vitu.utils.log_utils import logger
from vitu.utils.min_qty import get_min_order
from vitu.utils.output_utils import output
import numpy as np
 
np.set_printoptions(threshold=100000)
pd.set_option('display.max_columns',100000)
pd.set_option('display.width', 100000)
pd.set_option('display.max_colwidth',100000)


class Strategy(object):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            _instance = super(Strategy, cls).__new__(cls)
            cls._instance = _instance
        return cls._instance

    def __init__(self, initialize=None, handle_data=None, universe=None,
                 benchmark=None, freq=None, refresh_rate=None):
        """
        :param initialize: initialize
        :param handle_data: handle_data
        :param universe: ('BTC/USDT.okex', 'ETH/BTC.okex', 'XBT/USD.bitmex')
        :param benchmark: 'csi5'          # 策略参考标准
        :param freq: 'd',                 # 'd'日线回测，'m'15分钟线回测
        :param refresh_rate: 1 or (1,['08:00:00']) or (1,['08:00:00','18:00:00']),
        # 调仓时间间隔，若freq = 'd'的单位为交易日，若freq = 'm'时间间隔为分钟
        :param trigger_time: '08:00'      # 日级别调仓时间,时区为UTC
        """
        self.initialize = initialize
        self.handle_data = handle_data
        self.universe = universe
        self.benchmark = benchmark
        self.frequency = freq
        # self.refresh_rate = refresh_rate
        self.refresh_rate = refresh_rate[0] if isinstance(refresh_rate, (tuple)) else refresh_rate
        self.trigger_time = refresh_rate[1] if isinstance(refresh_rate, (tuple)) else None

        self.start = None
        self.end = None
        self.commission = None
        # self.asset_varieties = None
        self.portfolio = None
        self.context = None
        self.cache_data = None

        self.universe_assets = None
        self.all_assets = None

        self.total_dates = None
        self.strategy_dates = None

    def _initialize(self, strategy=None, start=None, end=None, timezone=None, commission=None):
        self.start = start
        self.end = end
        self.commission = commission
        self.timezone=timezone
        self.portfolio = Portfolio(strategy, start, end, commission,
                                   self.frequency, self.refresh_rate, self.trigger_time)
        self.context = self.portfolio.context

        # 最小精度
        self.context.min_order = {}
        for univ in self.universe:
            exchange = univ.split('.')[1]
            self.context.min_order[exchange] = {}
        # print(self.context.min_order)
        for univ in self.universe:
            exchange = univ.split('.')[1]
            symbol = univ.split('.')[0].lower()
            min_order_qty, min_order_amount = get_min_order(exchange, symbol)
            self.context.min_order[exchange][symbol] = {'min_order_qty':min_order_qty,
                                                             'min_order_amount':min_order_amount}


        # 记录universe所有的asset
        self.universe_assets = list()
        for univ in self.universe:
            base_asset = univ.split('.')[0].split('/')[0].lower()
            quote_asset = univ.split('.')[0].split('/')[1].lower()
            if base_asset not in self.universe_assets:
                self.universe_assets.append(base_asset)
            if quote_asset not in self.universe_assets:
                self.universe_assets.append(quote_asset)
        self.all_assets = list(set(AccountManager().asset_varieties + self.universe_assets))
        # print(self.all_assets)

        # # 初始每个账户添加除初始化之外的universe的asset
        # for name,account in self.portfolio.accounts.items():
        #     for asset in universe_assets:
        #         if asset not in account.current_position.keys():
        #             account.current_position[asset] = SpotPosition('spot', asset, 0, 0, 0, 0)

        self.total_dates = get_total_dates(self.frequency, 1, self.trigger_time, self.start, self.end)
        self.strategy_dates = get_total_dates(self.frequency, self.refresh_rate, self.trigger_time, self.start, self.end)
        if self.frequency in ['d','1d','day','1day']:
           self.day_date=get_day_dates(self.start, self.end,self.refresh_rate)
        else:
           self.day_date=get_day_dates(self.start, self.end)
        # 先输出report的dates信息，画图用
        #output({"display_type": "strategy",
          #    "dates":self.day_date})

        try:
            self.initialize(self.context)
        except Exception:
            output({"display_type": "error",
                    "error_msg": traceback.format_exc()})
            return 1

    async def _handle_data(self):
        # print("******************************************************************")
        clock = self.context.clock
        current_date = clock.current_date
        logger.current_date = current_date
        current_timestamp = clock.current_timestamp
        # print(current_date)
        prebars=clock.pre_bar

        pre_start = str(str2datetime(self.start) - datetime.timedelta(days=prebars))
        try:
            if not self.cache_data:
                self.cache_data = self.context.prepare_data(self.universe, self.all_assets, self.benchmark,
                                                                  self.frequency, pre_start, self.end, self.timezone)
        except Exception:
            output({"display_type": "error",
                    "error_msg": traceback.format_exc()})
            return 1

        # 记录初始持仓
        start = self.start + ' ' + self.trigger_time[0] if self.trigger_time else self.start # 只支持一个trigger_time
        if current_timestamp == str2timestamp(start):
            for name, account in self.portfolio.accounts.items():
                for asset, position in account.current_position.items():
                    position.context = self.context
            init_portfolio_position = dict()
            for asset in self.context.asset_varieties:
                init_pp_detail = PortfolioPosition(self.context, asset, self.portfolio.accounts).detail()
                init_portfolio_position[asset] = init_pp_detail

            self.context.init_portfolio_position = init_portfolio_position
            self.context.init_position_total = sum([asset['total_amount'] for asset in init_portfolio_position.values()])

            self.context.init_total_account_position = {}
            for name in self.context.accounts_name:
                name_position = "{}_position".format(name)
                total_amount = 0
                for asset,value in self.context.init_portfolio_position.items():
                    if name in value['consist_of'].keys():
                        total_amount += value['consist_of'][name]['amount']
                self.context.init_total_account_position[name_position] = total_amount

            # logger.info('【记录初始持仓时间】：{} s'.format(str(time.time() - start2)[:5]))

        try:
            if str(current_date) in self.strategy_dates:
                self.handle_data(self.context)
        except Exception:
            output({"display_type": "error",
                    "error_msg": traceback.format_exc()})
            return 1

        self.portfolio.record_history()

        # logger.info('【_handle_data耗时】：{} s'.format(str(time.time() - start2)[:5]))
        # print("******************************************************************", end='\n\n')

    def simple_report(self):
        report = SimpleReport(self.portfolio)
        simple_report = report.run()
        output(simple_report)

    def complete_report(self):
        report = CompleteReport(self.portfolio)
        complete_report = report.run()
        output(complete_report)

    def simplereport_excel(self):
        report = SimpleReport(self.portfolio)
        simple_report = report.run()
        output(simple_report)
        # 回测报告以excel表格形式输出
        workbook=xlwt.Workbook(encoding='utf-8')
        sheet1=workbook.add_sheet('sheet1',cell_overwrite_ok=True)
        c=0
        for key,value in simple_report.items():
            sheet1.write(0,c,key)
            if isinstance(value,list):
               s1=len(value)
               for s2 in range(0,s1):
                   temp=value[s2]
                   sheet1.write(s2+1,c,temp)  
            else:
                 sheet1.write(1,c,value)         
            c+=1
        root1=os.getcwd()    #获得当前目录路径，用来存放回测报告
        adress1=root1+'/'+'simple_report.xls' #保存报告的地址
        print(adress1)
        workbook.save(adress1)     
        #净值图形输出
        plt.plot(simple_report["cumulative_returns"])
        plt.title("Cumulative_returns",fontsize='large')
        plt.show()
        
    

if __name__ == '__main__':
    import time
    a = time.time()

    df_data = pd.read_csv('../data/static/binance_min_order.csv')
    print(df_data)

    symbol = 'BTC/USDT'
    base_asset = symbol.split('/')[0]
    quote_asset = symbol.split('/')[1]

    # 最小下单数量 0.000001BTC
    min_order_qty = df_data.loc[(df_data['baseAsset'] == base_asset) & (df_data['quoteAsset'] == quote_asset)][
        'minTradeAmount'].tolist()[0]
    print(min_order_qty)
    print(type(min_order_qty))
    # 最小下单金额 10USDT
    min_order_amount = df_data.loc[(df_data['baseAsset'] == base_asset) & (df_data['quoteAsset'] == quote_asset)][
        'minOrderValue'].tolist()[0]
    print(min_order_amount)
    print(type(min_order_amount))

    print(time.time()-a)
