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
from logging import Formatter
from logging.handlers import RotatingFileHandler


class HarvestLogger:

    LOG_NAME = 'harvest'
    LOG_FILE = '~/.harvest.log'
    LOG_FORMAT = '%(asctime)s - %(levelname)s :: %(message)s'

    @classmethod
    def setup(cls):
        if hasattr(cls, 'logger'):
            return
        cls.logger = logging.getLogger(cls.LOG_NAME)
        cls.logger.setLevel(logging.DEBUG)
        log_file = RotatingFileHandler(os.path.expanduser(cls.LOG_FILE),
                                       maxBytes=1048576, backupCount=3)
        log_file.setFormatter(Formatter(cls.LOG_FORMAT))
        cls.logger.addHandler(log_file)
        cls.logger.info('logger started.')

    @classmethod
    def log(cls, message):
        cls.logger.debug(message)
