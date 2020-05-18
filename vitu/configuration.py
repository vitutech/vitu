'''/*---------------------------------------------------------------------------------------------
 *  Copyright (c) VituTech. All rights reserved.
 *  Licensed under the Apache License 2.0. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/
'''
import os

class Config:

    @classmethod
    def tushare_token(cls):
        return os.environ.get('TUSHARE_TOKEN') or 'fb8f2489e74b45afc06d859d9a45ea48f424e6c87d971b0af724b261'

    @classmethod
    def heartbeat_timelength(cls):
        return int(os.environ.get('HEARTBEAT_TIMELENGTH') or '5') 

    @classmethod
    def bars_length(cls):
        return int(os.environ.get('BARS_LENGTH') or '45')

    @classmethod
    def bars_length_1m(cls):
        return int(os.environ.get('BARS_LENGTH_1M') or '2880')
    
    @classmethod
    def heartbeat_length_m(cls):
        return int(os.environ.get('HEARTBEAT_LENGTH_1M') or '300')
    
    @classmethod
    def bars_length_5m(cls):
        return int(os.environ.get('BARS_LENGTH_5M') or '576')
    

    @classmethod
    def benchmarks(cls):
        return (os.environ.get('BENCHMARK_VARIETIES') or 'csi5,csi6-20,csi21-100,csi100').split(',')

    @classmethod
    def mode(cls):
        return os.environ.get('MODE') or 'local'  # 'jupyter'

