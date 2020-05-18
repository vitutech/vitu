'''/*---------------------------------------------------------------------------------------------
 *  Copyright (c) VituTech. All rights reserved.
 *  Licensed under the Apache License 2.0. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/
'''
import pandas as pd
import numpy as np
import time
from datetime import datetime

from vitu.utils.date_utils import get_now_time, get_total_timestamps,get_total_dates
from vitudata.apis import get_bars

def get_data(exchange, symbol, frequency, start_date, end_date,timezone):
    data = get_bars(symbol, exchange, frequency=frequency, start_date=start_date, end_date=end_date,timezone=timezone)
    df_data = pd.DataFrame(data)
    # total_ts = get_total_timestamps(start_date, end_date)     #只能获得天的日期
    total_ts =get_total_dates(frequency,1,0,start_date, end_date)  #天或者分钟的日期，
    #对df_data清醒数据清洗
    if len(df_data)>1:
        if df_data['timestamp'][0]>0 and df_data['close'][0]>0:
           for x in range(1,len(df_data)):
               if df_data['close'][x]==0:
                  df_data.iloc[x,1:6]=df_data.iloc[x-1,1:6]

        else:
            nonzero=df_data[df_data['close']>0].index.tolist()
            if len(nonzero)>0:
                for n in range(0,nonzero[0]): 
                   df_data.iloc[n,1:6]=df_data.iloc[nonzero[0],1:6]
                for x in range(1,len(df_data)):
                    if df_data['high'][x]==0 and df_data['close'][x]==0:
                       df_data.iloc[x,1:6]=df_data.iloc[x-1,1:6]
     
    if len(df_data)==len(total_ts):
        df_data['timestamp'] = total_ts
    else:
        print('data error in cleaning, please wait')
        df_date=np.array(df_data['timestamp'] ,dtype='uint64')
        ts_date=[]
        for i in range(0,len(total_ts)):
            temp1=datetime.strptime(total_ts[i],'%Y-%m-%d %H:%M:%S').timestamp()
            ts_date.append(round(temp1)) #total_ts转化为时间戳形式 
        ts_date=np.array(ts_date,dtype='uint64')
        temp2=np.zeros([len(ts_date),5])
        df_data1=pd.DataFrame(temp2,index=range(len(ts_date)),columns=['open','high','low','close','volume'])    
        df_data1.insert(0,'timestamp',total_ts) #创建一个完整的dataframe,下面把df_data的值复制进去，再把没有的部分补上
        if len(df_data)<len(total_ts):
            x=len(df_data)-1
            start1=0
            while x>0 :
                  if df_date[x] != ts_date[x]:  
                      x-=1
                  elif df_date[x] == ts_date[x]: 
                       start1=x
                       break
            if start1>0:
               df_data1.iloc[0:start1,1:6]=df_data.iloc[0:start1,1:6]
               for j in range(start1,len(ts_date)):
                  if ts_date[j] in df_date:
                     loacte1=np.argwhere(df_date==ts_date[j])
                     df_data1.iloc[j,1:6]=df_data.iloc[int(loacte1[0]),1:6] 
                  else :
                       if j>0:
                          df_data1.iloc[j,1:6]=df_data1.iloc[j-1,1:6] 
            else:
                for j in range(0,len(ts_date)):
                   if ts_date[j] in df_date:
                      loacte1=np.argwhere(df_date==ts_date[j])
                      df_data1.iloc[j,1:6]=df_data.iloc[int(loacte1[0]),1:6] 
                   else :
                       if j>0:
                         df_data1.iloc[j,1:6]=df_data1.iloc[j-1,1:6] 
                      
        if len(df_data)>len(total_ts): 

           for j in range(0,len(ts_date)):
               if ts_date[j] in df_date:
                  loacte1=np.argwhere(df_date==ts_date[j])
                  df_data1.iloc[j,1:6]=df_data.iloc[int(loacte1[0]),1:6] 
               else :
                    if j>0:
                        df_data1.iloc[j,1:6]=df_data1.iloc[j-1,1:6] 
        df_data=df_data1         
    return df_data


if __name__ == '__main__':
    time_now = get_now_time()
    print(time_now)

    import time
    start = time.time()

    data = get_data('binance', 'btcusdt', '1d', '2017-10-01', '2019-12-05',0)
    print(data)

    print(time.time()-start)