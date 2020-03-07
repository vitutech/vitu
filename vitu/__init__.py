'''/*---------------------------------------------------------------------------------------------
 *  Copyright (c) VituTech. All rights reserved.
 *  Licensed under the Apache License 2.0. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/
'''
import os
from matplotlib.font_manager import FontProperties
from vitu.configuration import Config
from vitu.utils.log_utils import logger
# from vitu.data_api import API
# import vitu.vitudata as vitudata 


log = logger

font = None
dirName = os.path.dirname(os.path.abspath(__file__))
font = FontProperties(fname=os.path.join(dirName, 'wqy-microhei.ttc'), size=10)