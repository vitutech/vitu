'''/*---------------------------------------------------------------------------------------------
 *  Copyright (c) VituTech. All rights reserved.
 *  Licensed under the Apache License 2.0. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/
'''
import os

class Config:

    @classmethod
    def redis_host(cls):
        return os.environ.get('REDIS_HOST') or 'localhost'

    @classmethod
    def redis_port(cls):
        return int(os.environ.get('REDIS_PORT') or '6379')

    @classmethod
    def h5_root_dir(cls):
        return os.environ.get("H5_ROOT_DIR") or '/opt/data/vitu/bundle'


