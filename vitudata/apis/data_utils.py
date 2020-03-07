'''/*---------------------------------------------------------------------------------------------
 *  Copyright (c) VituTech. All rights reserved.
 *  Licensed under the Apache License 2.0. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/
'''
#!/usr/bin/env python
#coding:utf-8

'''
取数据相关接口
'''
import sys

import pytz

from vitudata.exceptions import ParamsError

if sys.version_info[0] == 3:
    xrange = range
    
import warnings
import datetime
import collections
import os
import re
import numpy as np


def is_str(s):
    return isinstance(s, six.string_types)

def is_list(l):
    return isinstance(l, (list, tuple))


def is_empty(container):
    """ 检查容器类数据不为空 dict, set, list, queue ..."""
    return len(container) == 0


import six


def check_string(s):
    assert is_str(s), "参数必须是个字符串, 实际是:%s" % str(type(s))


def check_list(l):
    assert isinstance(l, (tuple, list)), "参数必须是tuple或者list, 实际是: %s" % str(type(l))


def ensure_str_tuple(args):
    if is_str(args):
        return (args,)
    else:
        atuple = tuple(args)
        for i in atuple:
            assert isinstance(i, six.string_types)
        return atuple


def date2dt(date):
    return datetime.datetime.combine(date, datetime.time.min)


def convert_dt(dt):
    if is_str(dt):
        if ':' in dt:
            return datetime.datetime.strptime(dt, '%Y-%m-%d %H:%M:%S').replace(tzinfo=pytz.timezone('utc'))
        else:
            return datetime.datetime.strptime(dt, '%Y-%m-%d').replace(tzinfo=pytz.timezone('utc'))
    elif isinstance(dt, datetime.datetime):
        if dt.tzinfo is None:
            dt.replace(tzinfo=pytz.timezone('utc'))
        return dt
    elif isinstance(dt, datetime.date):
        if dt.tzinfo is None:
            dt.replace(tzinfo=pytz.timezone('utc'))
        return date2dt(dt)
    raise ParamsError("date 必须是datetime.date, datetime.datetime或者如下格式的字符串:'2018-10-05'")


def convert_date(date):
    if is_str(date):
        if ':' in date:
            date = date[:10]
        return datetime.datetime.strptime(date, '%Y-%m-%d').date()
    elif isinstance(date, datetime.datetime):
        return date.date()
    elif isinstance(date, datetime.date):
        return date
    raise ParamsError("date 必须是datetime.date, datetime.datetime或者如下格式的字符串:'2018-10-05'")


def all_is_none(*args):
    for obj in args:
        if obj is not None:
            return False
    return True


def all_not_none(*args):
    for obj in args:
        if obj is None:
            return False
    return True
