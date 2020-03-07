'''/*---------------------------------------------------------------------------------------------
 *  Copyright (c) VituTech. All rights reserved.
 *  Licensed under the Apache License 2.0. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/
'''
error = (lambda code, message: {'code': code, 'data': message})

class BacktestInputError(Exception):
    """回测参数输入异常"""
    pass

class BacktestError(Exception):
    """回测异常"""
    pass

class Errors(object):
    """
    Enumerate errors.
    """
    INVALID_START_DATE = BacktestInputError(error(500, '回测 start 日期不合法'))
    INVALID_END_DATE = BacktestInputError(error(500, '回测 end 不合法'))
    INVALID_START_END = BacktestInputError(error(500, '开始日期晚于结束日期'))
    INVALID_DATE = BacktestInputError(error(500, '日期不合法'))
    INVALID_TRADING_DAYS = BacktestInputError(error(500, '回测区间日期索引不到'))
    INVALID_FREQ = BacktestInputError(error(500, '回测 freq 不合法'))

    INVALID_PRICE = BacktestError(error(500, '下单价格不合法'))
    INVALID_AMOUNT = BacktestError(error(500, '下单数量不合法'))


