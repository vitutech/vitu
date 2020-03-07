'''/*---------------------------------------------------------------------------------------------
 *  Copyright (c) VituTech. All rights reserved.
 *  Licensed under the Apache License 2.0. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/
'''
class Universe(object):
    def get(self, query=None):
        pass

class StaticUniverse(Universe):
    def __init__(self, universe=None):
        if universe:
            self.universe = universe
        else:
            self.universe = list()

    def get(self, query=None):
        return self.universe


class IndexUniverse(Universe):
    def __init__(self, index):
        self.index = index

    def get(self, query=None):
        pass


if __name__ == '__main__':
    # universe.get(query={"filter_type": "volume", "order": "desc", "limit": "5"})
    u1 = StaticUniverse(['BTC/USDT.binance'])
    universe = u1.get()
    print(universe)