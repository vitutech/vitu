# 可以自己import我们平台支持的第三方python模块，比如pandas、numpy等。
from vitu import ai, log
import numpy as np
import os
#配置数据导入地址
os.environ["H5_ROOT_DIR"]="/home/john/Downloads/datah5/bundle" #"D:/datah5_m/bundle"
print(os.path.exists(os.environ["H5_ROOT_DIR"]))  #返回True，则数据导入成功

# 配置单/多账户初始持仓信息，name字段区分
ai.create_account(name='account1', exchange='binance', account_type='digital.spot',
                  position_base=[{'asset': 'BTC', 'qty': 100},{'asset': 'USDT', 'qty': 50000}])

# 在这个方法中编写任何的初始化逻辑，context对象将会在你的算法策略的任何方法之间做传递
def initialize(context):
    context.N = 20
    context.k = 2
    context.account = context.get_account('account1')

# 你选择的universe crypto的数据更新将会触发此段逻辑，例如日线历史数据或者是实时数据更新
def handle_data(context):
    # 开始编写你的主要的算法逻辑

    # 读取历史数据
    close_price = context.history('BTC/USDT.binance', 'close', bars=20, rtype='ndarray')
    # MB中轨：N日的简单移动平均
    # UP上轨：中轨 + k倍N日标准差
    # DN下轨：中轨 - k倍N日标准差
    MA = np.mean(close_price[-context.N+1:])
    MD = np.sqrt(sum([(i-MA)**2 for i in close_price])/len(close_price))
    MB = np.mean(close_price[-context.N+1:])
    UP = MB + context.k*MD
    DN = MB - context.k*MD
    # print(MA, MD, UP, MB, DN)

    # 获取最新价格
    current_price = context.get_price("BTC/USDT.binance")
    # 如果收盘价下穿布林中轨时，则卖出
    if close_price[-2] < UP and close_price[-1] > UP:
        context.account.sell("BTC/USDT.binance", current_price, 0.2)
    # 如果收盘价上穿布林上轨时，则买入
    elif close_price[-2] > DN and close_price[-1] < DN:
        context.account.buy("BTC/USDT.binance", current_price, 0.2)

# 可以直接指定universe，或者通过筛选条件选择universe池
universe = ai.create_universe(['BTC/USDT.binance'])

# 配置策略参数如：基准、回测数据级别等
my_strategy = ai.create_strategy(
    initialize,
    handle_data,
    universe=universe,
    benchmark='csi5',
    freq='d',
    refresh_rate=1
)

# 配置回测参数如：回测日期、手续费率
ai.backtest(
    strategy=my_strategy,
    start='2018-10-10',
    end='2019-08-10',
    commission={'taker': 0.0002, 'maker': 0.0002}
)