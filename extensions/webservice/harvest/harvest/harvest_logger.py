# Copyright (c) 2013 Martin Abente Lahaye. - tch@sugarlabs.org
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA

import os
import logging
from logging import Logger
from logging import Formatter
from logging.handlers import RotatingFileHandler


_logger = None


class HarvestLogger(Logger):

    LOG_NAME = 'harvest'
    LOG_FILE = '~/.harvest/log'
    LOG_FORMAT = '%(created)f %(levelname)s %(name)s: %(message)s'
    LOG_COUNT = 1
    LOG_SIZE = 1048576
    LOG_LEVEL = 'SUGAR_LOGGER_LEVEL'

    def __init__(self):
        level = logging.INFO
        if self.LOG_LEVEL in os.environ and \
           os.environ[self.LOG_LEVEL] == 'debug':
            level = logging.DEBUG

        Logger.__init__(self, self.LOG_NAME, level)

        log_file = RotatingFileHandler(os.path.expanduser(self.LOG_FILE),
                                       maxBytes=self.LOG_SIZE,
                                       backupCount=self.LOG_COUNT)
        log_file.setFormatter(Formatter(self.LOG_FORMAT))
        self.addHandler(log_file)


def get_logger():
    global _logger
    if _logger is None:
        _logger = HarvestLogger()
    return _logger
