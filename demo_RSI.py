from vitu import ai
import numpy as np
import talib
import os
#配置数据导入地址
os.environ["H5_ROOT_DIR"]="/home/john/Downloads/datah5/bundle" #"I:/datah5/bundle"
print(os.path.exists(os.environ["H5_ROOT_DIR"]))  #返回True，则数据导入成功

ai.create_account(name='RSI', exchange='binance', account_type='digital.spot',position_base=[{'asset': 'USDT', 'qty': 50000}])
universe = ai.create_universe(['BTC/USDT.binance'])


def initialize(context):
    context.account = context.get_account('RSI')
    context.LOW_RSI = 20
    context.HIGH_RSI = 80
    context.rsi_list = []

    
def handle_data(context):
    history = context.history('BTC/USDT.binance', ['close'], bars=15, rtype='dataframe')
    
    rsi = talib.RSI(history['close'].values, timeperiod=14)[-1]
    print(rsi)
       
    position_btc = context.account.get_position('BTC')
    current_available_btc = position_btc['available']
    
    position_usdt = context.account.get_position('USDT')
    current_available_usdt = position_usdt['available']
      
    current_price = context.get_price('BTC/USDT.binance')
   
    # 当RSI信号小于30，且拥有的BTC数量大于0时，卖出所有BTC
    if rsi < context.LOW_RSI and current_available_btc > 0:
      context.account.sell_pct('BTC/USDT.binance', current_price, 1)
    # 当RSI信号大于70, 且拥有的USDT数量为0时，则全仓买入
    elif rsi > context.HIGH_RSI and current_available_usdt > 0:
      context.account.buy_pct('BTC/USDT.binance', current_price, 1)
      
my_strategy = ai.create_strategy(
    initialize,
    handle_data,
    universe=universe,
    benchmark='csi5',
    freq='d',
    refresh_rate=1,
)


ai.backtest(strategy=my_strategy,
        start='2017-09-01',
        end='2019-11-30',
        commission={'taker': 0.001, 'maker': 0.001}
)