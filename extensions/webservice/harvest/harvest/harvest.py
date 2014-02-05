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
import time
import random
import urlparse

from gi.repository import GConf
from gi.repository import Soup

from .crop import Crop
from .errors import MissingInfoError
from .errors import NotSelectedError
from .errors import TooSoonError
from .errors import NothingNewError
from .errors import SendError
from .errors import NoCharacteristicsError
from .harvest_logger import get_logger


class Harvest(object):

    DELAY = 2700
    OFFSET = 1800
    WEEKLY = 604800
    MONTHLY = 2592000
    SKIPS = 3

    ENDPOINT = '/rpc/store'
    NOT_ENABLED = '/desktop/sugar/collaboration/harvest_not_enabled'
    FREQUENCY = '/desktop/sugar/collaboration/harvest_frequency'
    TIMESTAMP = '/desktop/sugar/collaboration/harvest_timestamp'
    RETRY = '/desktop/sugar/collaboration/harvest_retry'
    HOSTNAME = '/desktop/sugar/collaboration/harvest_hostname'
    API_KEY = '/desktop/sugar/collaboration/harvest_api_key'
    WORKING_PATH = '~/.harvest/'
    CROP_FILE = 'crop'
    VERSION_FILE = 'crop.version'

    def __init__(self):
        path = os.path.expanduser(self.WORKING_PATH)
        if not os.path.exists(path):
            os.makedirs(path, 0755)

        self._crop_path = os.path.join(path, self.CROP_FILE)
        self._version_path = os.path.join(path, self.VERSION_FILE)
        self._logger = get_logger()

        client = GConf.Client.get_default()
        self._not_enabled = client.get_bool(self.NOT_ENABLED)
        self._frequency = client.get_int(self.FREQUENCY) or self.WEEKLY
        self._timestamp = client.get_int(self.TIMESTAMP)
        self._retry_timestamp = client.get_int(self.RETRY)
        self._hostname = client.get_string(self.HOSTNAME)
        self._api_key = client.get_string(self.API_KEY)

    def is_not_enabled(self):
        if self._not_enabled is True:
            self._logger.debug('automatic collection is not enabled')
            return True
        return False

    def _save_time(self, path, timestamp):
        client = GConf.Client.get_default()
        client.set_int(path, timestamp)

    def _selected(self):
        """ randomly determines if it will collect or not """
        return (not random.randrange(0, self.SKIPS))

    def _ready(self, timestamp):
        return (timestamp > self._timestamp + self._frequency)

    def _retry_ready(self, timestamp):
        return (timestamp >= self._retry_timestamp)

    def _retry_in(self, timestamp):
        """ retry allowed between 45 and 75 minutes since timestamp """
        return (timestamp + self.DELAY + (self.OFFSET * random.random()))

    def _send(self, data):
        uri = Soup.URI.new(urlparse.urljoin(self._hostname, self.ENDPOINT))
        message = Soup.Message(method='POST', uri=uri)
        message.request_headers.append('x-api-key', self._api_key)
        message.set_request('application/json',
                            Soup.MemoryUse.COPY,
                            data, len(data))

        session = Soup.SessionSync()
        session.add_feature_by_type(Soup.ProxyResolverDefault)
        session.send_message(message)

        if message.status_code == 200:
            return True
        self._logger.debug('could not send data: %d', message.status_code)
        return False

    def _retry_valid(self):
        if not os.path.exists(self._crop_path):
            return False
        # don't use it if not sure about the version
        if not os.path.exists(self._version_path):
            os.remove(self._crop_path)
            return False
        with open(self._version_path, 'r') as file:
            version = file.read()
        if version != Crop.VERSION:
            os.remove(self._crop_path)
            os.remove(self._version_path)
            return False
        return True

    def _save_crop(self, crop, timestamp):
        with open(self._crop_path, 'w') as file:
            file.write(crop)
        with open(self._version_path, 'w') as file:
            file.write(Crop.VERSION)
        os.utime(self._crop_path, (timestamp, timestamp))
        self._logger.debug('saved crop to %s.' % self._crop_path)

    def _restore_crop(self):
        timestamp = os.stat(self._crop_path).st_mtime
        with open(self._crop_path, 'r') as file:
            crop = file.read()
        os.remove(self._version_path)
        os.remove(self._crop_path)
        self._logger.debug('restored crop from %s.' % self._crop_path)
        return crop, timestamp

    def _do_collect(self, timestamp):
        self._logger.debug('collecting crop.')
        crop = Crop(start=self._timestamp, end=timestamp)

        # do not collect it, if we already know it will be rejected
        if not crop.characterizable():
            self._logger.debug('missing learner characteristics.')
            raise NoCharacteristicsError()

        crop.collect()
        if not crop.grown():
            self._logger.debug('nothing new has grown.')
            raise NothingNewError()
        return crop.serialize()

    def collect(self, forced=False):
        self._logger.debug('triggered.')

        if not self._hostname or not self._api_key:
            self._logger.error('server information is missing')
            raise MissingInfoError()

        if not forced and not self._selected():
            self._logger.debug('skipped this time.')
            raise NotSelectedError()

        timestamp = int(time.time())
        if not self._ready(timestamp):
            self._logger.debug('it is too soon for collecting again.')
            raise TooSoonError()

        if not forced and not self._retry_ready(timestamp):
            self._logger.debug('it is too soon for trying again.')
            raise TooSoonError()
        self._save_time(self.RETRY, self._retry_in(timestamp))

        if self._retry_valid():
            crop, timestamp = self._restore_crop()
        else:
            crop = self._do_collect(timestamp)

        if not self._send(crop):
            self._save_crop(crop, timestamp)
            raise SendError()
        self._save_time(self.TIMESTAMP, timestamp)
        self._logger.info('successfully collected.')
