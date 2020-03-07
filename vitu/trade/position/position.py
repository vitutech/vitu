'''/*---------------------------------------------------------------------------------------------
 *  Copyright (c) VituTech. All rights reserved.
 *  Licensed under the Apache License 2.0. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/
'''
class Position(object):
    __slots__ = [
        'asset_class',
        'asset',
    ]
    def __init__(self, asset_class, asset):
        self.asset_class = asset_class
        self.asset = asset

    def __getitem__(self, key, default=None):
        item_value = self.__getattribute__(key) if self.__getattribute__(key) else default
        return item_value

















