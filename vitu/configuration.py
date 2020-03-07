'''/*---------------------------------------------------------------------------------------------
 *  Copyright (c) VituTech. All rights reserved.
 *  Licensed under the Apache License 2.0. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/
'''
import os

class Config:


    @classmethod
    def bars_length(cls):
        return int(os.environ.get('BARS_LENGTH') or '45')

    @classmethod
    def benchmarks(cls):
        return (os.environ.get('BENCHMARK_VARIETIES') or 'csi5,csi6-20,csi21-100,csi100').split(',')

    @classmethod
    def mode(cls):
        return os.environ.get('MODE') or 'local'  # 'jupyter'

