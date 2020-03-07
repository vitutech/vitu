'''/*---------------------------------------------------------------------------------------------
 *  Copyright (c) VituTech. All rights reserved.
 *  Licensed under the Apache License 2.0. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/
'''
#!/usr/bin/env python
#coding:utf-8


class UserError(Exception):
    # 用户代码导致的相关异常
    pass


class InternalError(Exception):
    # 系统内部的异常
    pass


class ParamsError(UserError):
    # 用户传入的api参数不合理
    pass


class SymbolNotSupported(UserError):
    # 用户尝试使用标的不支持
    pass


class MissDataError(InternalError):
    # 数据缺失导致的异常
    pass


class InitObjError(InternalError):
    # 常用于初始化对象时由于内部错误（比如数据错误）抛出的异常
    pass


class InvalidDataError(InternalError):
    # 数据不正常抛出的异常
    pass


class TimeoutError(InternalError):
    # 超时时触发的异常
    pass
