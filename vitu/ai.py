'''/*---------------------------------------------------------------------------------------------
 *  Copyright (c) VituTech. All rights reserved.
 *  Licensed under the Apache License 2.0. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/
'''

import time
import asyncio

from vitu.account.account_manager import AccountManager
from vitu.strategy.strategy import Strategy
from vitu.universe.universe import StaticUniverse, IndexUniverse
from vitu.configuration import Config
from vitu.utils.output_utils import output

def create_account(name=None, exchange=None, account_type=None, position_base=None):
    """
    :param name: 'spot_account'
    :param exchange: 'binance'
    :param account_type: 'digital.spot'
    :param position: ({'asset': 'BTC', 'qty': 100}, {'asset': 'USDT', 'qty': 200000}))
    :return: AccountManager instance
    """
    AccountManager().config(name, exchange, account_type, position_base)


def create_strategy(initialize=None, handle_data=None, universe=None, benchmark=None,
                    freq=None, refresh_rate=None):
    """
    :param initialize: initialize
    :param handle_data: handle_data
    :param universe: ['BTC/USDT.okex', 'ETH/BTC.okex', 'XBT/USD.bitmex']
    :param benchmark: 'csi5'/'btc'
    :param freq: 'd'
    :param refresh_rate: 1 or (1,['08:00:00']) or (1,['08:00:00','18:00:00'])
    :return: strategy_instance
    """
    return Strategy(initialize, handle_data, universe, benchmark, freq, refresh_rate)


def create_universe(universe=None):
    """
    :param universe: ['BTC/USDT.okex', 'ETH/BTC.okex']/'csi5'
    :return:
    """
    if universe:
        if universe in Config.benchmarks():
            return IndexUniverse(universe).get()
        else:
            return StaticUniverse(universe).get()

error_complete = 0

# async def _heartbeat(strategy):
#     global error_complete
#     try:
#         while True:
            
#             clock = strategy.portfolio.context.clock
#             timenow=time.time()
#             if (timenow-clock.datestart)> Config.heartbeat_timelength():
#                 clock.reset_datestart()
#                 output('heartbeating')
#             await asyncio.sleep(0)
#             if error_complete == 1:
#                 return
#             if clock.current_timestamp > clock.end_timestamp:
#                 break
#     except Exception as e:
#         error_complete = 1
#         raise e
async def _handle(strategy):
    global error_complete
    try:
        while True:
            clock = strategy.portfolio.context.clock
            timenow=time.time()
            if (timenow-clock.datestart)> Config.heartbeat_timelength():
                clock.reset_datestart()
                output('heartbeating')
            if error_complete == 1:
                return
            if clock.current_timestamp > clock.end_timestamp:
                break
            error_complete = await strategy._handle_data()
            clock.next()
            await asyncio.sleep(0)
    except Exception as e:
        error_complete = 1
        raise e

async def _report(strategy):
    global error_complete
    try:
        while True:
            await asyncio.sleep(1)
            if error_complete == 1:
                return
            clock = strategy.portfolio.context.clock
            if clock.current_timestamp > clock.end_timestamp:
                clock.run_end = time.time()
                strategy.portfolio.context.completed_time = round(clock.run_end - clock.run_start,4)
                # print('【handle总耗时】：{} s'.format(strategy.portfolio.context.completed_time))
                # strategy.simple_report()
                #strategy.complete_report()
                strategy.simplereport_excel()
                break


            if strategy.frequency in ['d','1d','day','1day'] :
               if clock.bars > Config.bars_length():  
                  clock.reset_bars()
                  strategy.simple_report()
            elif strategy.frequency in ['m','1m','min','minute'] :
               if clock.bars >Config.bars_length_1m():  
                  clock.reset_bars()
                  strategy.simple_report()


            elif strategy.frequency in ['5m','5mins','5minutes'] :
               if clock.bars >Config.bars_length_5m():  
                  clock.reset_bars()
                  strategy.simple_report()
         
    except Exception as e:
        error_complete = 1
        raise e


def backtest(strategy, start, end, commission, timezone=1):
    """
    :param strategy: strategy
    :param start: '2019-06-01'  # 回测起始时间
    :param end: '2019-07-01'    # 回测结束时间
    :param commission: {'buy': 0.001, 'sell': 0.001, 'open': 0.001, 'close': 0.001}
    :return: portfolio
    :timezone:timezone
    """
    global error_complete
    error_complete = 0
    strategy._initialize(strategy, start, end, timezone, commission)
    loop = asyncio.get_event_loop()
    if Config.mode() == 'jupyter':
        loop.create_task(_handle(strategy))
        loop.create_task(_report(strategy))
    else:
        loop.run_until_complete(asyncio.gather(_handle(strategy), _report(strategy))) #_heartbeat(strategy),
        loop.close()



