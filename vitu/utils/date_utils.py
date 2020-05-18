'''/*---------------------------------------------------------------------------------------------
 *  Copyright (c) VituTech. All rights reserved.
 *  Licensed under the Apache License 2.0. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/
'''
import datetime

def get_now_time():
    now_time = str(datetime.datetime.now()).split('.')[0]
    return now_time

def str2datetime(str_date):
    if len(str_date) == 10:
        return datetime.datetime.strptime(str_date, '%Y-%m-%d')
    elif len(str_date) == 19:
        return datetime.datetime.strptime(str_date, '%Y-%m-%d %H:%M:%S')
    elif len(str_date) == 26:
        return datetime.datetime.strptime(str_date, '%Y-%m-%dT%H:%M:%S.%f')
    elif len(str_date) == 28:
        str_date = str_date.split('+')[0]
        return datetime.datetime.strptime(str_date, '%Y-%m-%dT%H:%M:%S.%f')

def datetime2timestamp(date):
    return datetime.datetime.timestamp(date)

def str2timestamp(str_date):
    if len(str_date) == 10:
        return datetime.datetime.timestamp(datetime.datetime.strptime(str_date, '%Y-%m-%d'))
    elif len(str_date) == 19:
        return datetime.datetime.timestamp(datetime.datetime.strptime(str_date, '%Y-%m-%d %H:%M:%S'))
    elif len(str_date) == 26:
        return datetime.datetime.timestamp(datetime.datetime.strptime(str_date, '%Y-%m-%dT%H:%M:%S.%f'))
    elif len(str_date) == 28:
        str_date = str_date.split('+')[0]
        return datetime.datetime.timestamp(datetime.datetime.strptime(str_date, '%Y-%m-%dT%H:%M:%S.%f'))

def timestamp2str(timestamp):
    return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

def get_total_dates(frequency, refresh_rate, trigger_time, start, end):
    if trigger_time:
        start = start + ' ' + trigger_time[0]  # 只支持一个trigger_time
        end = end + ' ' + trigger_time[0]
    start_date = str2datetime(start)
    end_date = str2datetime(end)
    date = list()
    if frequency in ['d','1d','day','daily']:
        while True:
            if start_date <= end_date:
                date.append(str(start_date))
                start_date += datetime.timedelta(days=refresh_rate)
                # start_date += datetime.timedelta(days=1)
            else:
                break
    elif frequency in ['m','1m','min','minute']:
        while True:
            if start_date <= end_date:
                date.append(str(start_date))
                start_date += datetime.timedelta(minutes=refresh_rate)
                # start_date += datetime.timedelta(minutes=1)
            else:
                break
    elif frequency in ['5m','5min','5minutes']:
        while True:
            if start_date <= end_date:
                date.append(str(start_date))
                start_date += datetime.timedelta(minutes=5*refresh_rate)
                # start_date += datetime.timedelta(minutes=1)
            else:
                break
    return date
def get_day_dates(start_date, end_date,refresh_rate=1):
    start_date = str2datetime(start_date)
    end_date = str2datetime(end_date)
    daydate_list = list()
    while True:
        if start_date <= end_date:
            daydate_list.append(str(start_date))
            start_date += datetime.timedelta(days=refresh_rate)
        else:
            break
    return daydate_list

def get_total_timestamps(start_date, end_date):
    start_date = str2datetime(start_date)
    end_date = str2datetime(end_date)
    timestamp_list = list()
    while True:
        if start_date <= end_date:
            timestamp_list.append(round(datetime.datetime.timestamp(start_date)))
            start_date += datetime.timedelta(days=1)
        else:
            break
    return timestamp_list

def get_dates_length(start, end):
    start_date = str2datetime(start)
    end_date = str2datetime(end)
    length = end_date - start_date
    return length.days+1


if __name__ == '__main__':
    start = '2019-02-05'
    end = '2019-02-08'
    a = str2datetime(start)
    print(a.date())

