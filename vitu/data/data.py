'''/*---------------------------------------------------------------------------------------------
 *  Copyright (c) VituTech. All rights reserved.
 *  Licensed under the Apache License 2.0. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/
'''
import pandas as pd

from vitu.utils.date_utils import get_now_time, get_total_timestamps
from vitudata.apis import get_bars

def get_data(exchange, symbol, frequency, start_date, end_date):
    data = get_bars(symbol, exchange, frequency=frequency, start_date=start_date, end_date=end_date)
    df_data = pd.DataFrame(data)
    total_ts = get_total_timestamps(start_date, end_date)
    df_data['timestamp'] = total_ts
    return df_data


if __name__ == '__main__':
    time_now = get_now_time()
    print(time_now)

    import time
    start = time.time()

    data = get_data('binance', 'btcusdt', '1d', '2017-10-01', '2019-12-05')
    print(data)

    print(time.time()-start)