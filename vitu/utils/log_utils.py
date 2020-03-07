'''/*---------------------------------------------------------------------------------------------
 *  Copyright (c) VituTech. All rights reserved.
 *  Licensed under the Apache License 2.0. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/
'''
class Logger(object):
    def __init__(self):
        self.current_date = None

    def debug(self, message):
        print(self.current_date, '[DEBUG]', message)

    def info(self, message):
        print(self.current_date, '[INFO]', message)

    def warning(self, message):
        print(self.current_date, '[WARNING]', message)

    def error(self, message):
        print(self.current_date, '[ERROR]', message)

    def critical(self, message):
        print(self.current_date, '[CRITICAL]', message)

logger = Logger()