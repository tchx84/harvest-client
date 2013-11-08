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

import time
import random
import json
import urllib2
import urlparse

from gi.repository import GConf

from .crop import Crop
from .errors import TooSoonError
from .errors import NothingNewError
from .errors import SendError
from .harvest_logger import HarvestLogger


class Harvest(object):

    RETRY = 3600
    WEEKLY = 604800
    MONTHLY = 2592000
    SKIPS = 3

    ENDPOINT = '/rpc/store'
    FREQUENCY = '/desktop/sugar/collaboration/harvest_frequency'
    TIMESTAMP = '/desktop/sugar/collaboration/harvest_timestamp'
    ATTEMPT = '/desktop/sugar/collaboration/harvest_attempt'
    HOSTNAME = '/desktop/sugar/collaboration/harvest_hostname'
    API_KEY = '/desktop/sugar/collaboration/harvest_api_key'

    def __init__(self):
        HarvestLogger.setup()
        client = GConf.Client.get_default()
        self._frequency = client.get_int(self.FREQUENCY) or self.WEEKLY
        self._timestamp = client.get_int(self.TIMESTAMP)
        self._attempt = client.get_int(self.ATTEMPT)
        self._hostname = client.get_string(self.HOSTNAME)
        self._api_key = client.get_string(self.API_KEY)

    def _save_time(self, path, timestamp):
        client = GConf.Client.get_default()
        client.set_int(path, timestamp)

    def _selected(self):
        """ randomly determines if it will collect or not """
        return (not random.randrange(0, self.SKIPS))

    def _ready(self, timestamp):
        return (timestamp > self._timestamp + self._frequency)

    def _retry(self, timestamp):
        return (timestamp > self._attempt + self.RETRY)

    def _send(self, data):
        headers = {'x-api-key': self._api_key,
                   'Content-Type': 'application/json'}
        url = urlparse.urljoin(self._hostname, self.ENDPOINT)

        info = None
        req = urllib2.Request(url, data, headers)
        try:
            response = urllib2.urlopen(req)
            info = json.loads(response.read())
        except Exception as err:
            HarvestLogger.log(err)
            return False

        return isinstance(info, dict) and \
            'success' in info and \
            info['success'] is True

    def collect(self, forced=False):
        HarvestLogger.log('triggered.')

        if not forced and not self._selected():
            HarvestLogger.log('skipped this time.')
            return

        timestamp = int(time.time())
        if not self._ready(timestamp):
            HarvestLogger.log('it is too soon for collecting again.')
            raise TooSoonError()

        if not forced and not self._retry(timestamp):
            HarvestLogger.log('it is too soon for trying again.')
            raise TooSoonError()
        self._save_time(self.ATTEMPT, timestamp)

        crop = Crop(start=self._timestamp, end=timestamp)
        crop.collect()

        if not crop.grown():
            HarvestLogger.log('nothing new has grown.')
            raise NothingNewError()

        if not self._send(crop.serialize()):
            raise SendError()
        self._save_time(self.TIMESTAMP, timestamp)
        HarvestLogger.log('successfully collected.')
