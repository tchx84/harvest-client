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
import json
import urllib2
import urlparse
import logging

from gi.repository import GConf

from crop import Crop


class Harvest(object):

    WEEKLY = 604800
    MONTHLY = 2592000
    ENDPOINT = '/rpc/store'
    FREQUENCY = '/desktop/sugar/collaboration/harvest_frequency'
    TIMESTAMP = '/desktop/sugar/collaboration/harvest_timestamp'
    HOSTNAME = '/desktop/sugar/collaboration/harvest_hostname'
    API_KEY = '/desktop/sugar/collaboration/harvest_api_key'
    TOO_SOON = 0
    NOTHING = 1
    OK = 2
    ERROR = 3

    def __init__(self):
        client = GConf.Client.get_default()
        self._frequency = client.get_int(self.FREQUENCY) or self.WEEKLY
        self._timestamp = client.get_int(self.TIMESTAMP)
        self._hostname = client.get_string(self.HOSTNAME)
        self._api_key = client.get_string(self.API_KEY)

    def _save_timestamp(self, timestamp):
        client = GConf.Client.get_default()
        self._last_timestamp = client.set_int(self.TIMESTAMP, timestamp)

    def _ready(self, timestamp):
        return (timestamp > self._timestamp + self._frequency)

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
            logging.error(err)
            return False

        return isinstance(info, dict) and \
            'success' in info and \
            info['success'] is True

    def collect(self):
        timestamp = int(time.time())
        if not self._ready(timestamp):
            logging.error('harvest: It is too soon for collecting again.')
            return self.TOO_SOON

        crop = Crop(start=self._timestamp, end=timestamp)
        crop.collect()
        if not crop.grown():
            logging.error('harvest: Nothing new has grown.')
            return self.NOTHING

        if self._send(crop.serialize()):
            self._save_timestamp(timestamp)
            return self.OK

        return self.ERROR