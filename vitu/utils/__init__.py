'''/*---------------------------------------------------------------------------------------------
 *  Copyright (c) VituTech. All rights reserved.
 *  Licensed under the Apache License 2.0. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/
'''
import os
from matplotlib.font_manager import FontProperties
# from vitu.data_api import API
from vitu.configuration import Config

# api = API(Config.tushare_token())

font = None
dirName = os.path.dirname(os.path.abspath(__file__))
font = FontProperties(fname=os.path.join(dirName, 'wqy-microhei.ttc'), size=10)