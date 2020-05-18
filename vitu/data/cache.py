'''/*---------------------------------------------------------------------------------------------
 *  Copyright (c) VituTech. All rights reserved.
 *  Licensed under the Apache License 2.0. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/
'''
from vitu.utils.date_utils import str2timestamp

class DataCache(object):
    def __init__(self):
        self.data = dict()

    def get_daily_ohlcv(self, k_lines_key, start, end, attributes):
        """
        :param k_lines_key: 'spot-binance-btcusdt'
        :param start_date: datetime
        :param end_date: datetime
        :return: dataframe
        """
        # start_ts = str(start)
        # end_ts = str(end)
        total_data = self.data[k_lines_key]
        data = total_data.loc[start:end-1,attributes] #total_data.iloc[start:end,:][attributes] 
        return data


