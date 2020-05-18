'''/*---------------------------------------------------------------------------------------------
 *  Copyright (c) VituTech. All rights reserved.
 *  Licensed under the Apache License 2.0. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/
'''
from vitu.configuration import Config
from IPython.display import display
from pprint import pprint
import numpy as np
import pandas as pd
pd.set_option('display.max_rows',None)
pd.set_option('display.max_columns',None)
np.set_printoptions(threshold=10000000)
 

def output(report):
    if Config.mode() == 'jupyter':
        display(report)

    else:
        if isinstance(report,dict):
            for key,value in report.items():
                print(key,value)
        else:
            print(report)