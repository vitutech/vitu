import os
from matplotlib.font_manager import FontProperties
# from vitu.data_api import API
from vitu.configuration import Config
from vitu.utils.log_utils import logger

# api = API(Config.tushare_token())s
log = logger

font = None
dirName = os.path.dirname(os.path.abspath(__file__))
font = FontProperties(fname=os.path.join(dirName, 'wqy-microhei.ttc'), size=10)