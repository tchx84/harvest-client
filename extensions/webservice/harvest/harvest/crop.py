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
import json
import hashlib

from gi.repository import GConf

from sugar3.datastore import datastore


class CropErrorNotReady:
    pass


class Crop(object):

    ARM_SN_PATH = '/ofw/serial-number/serial-number'
    X86_SN_PATH = '/proc/device-tree/serial-number'
    AGE_PATH = '/desktop/sugar/user/birth_timestamp'
    GENDER_PATH = '/desktop/sugar/user/gender'

    def __init__(self, start=None, end=None):
        self._start = start
        self._end = end
        self._data = None

    def serialize(self):
        if not self._data:
            raise CropErrorNotReady()
        return json.dumps(self._data)

    def grown(self):
        if not self._data:
            raise CropErrorNotReady()
        if not self._data[1].keys():
            return False
        return True

    def collect(self):
        self._data = []
        self._data.append(self._learner())
        self._data.append(self._activities())

    def _learner(self):
        learner = []
        learner.append(self._serial_number())
        learner.append(self._age())
        learner.append(self._gender())
        return learner

    def _serial_number(self):
        path = None
        if os.path.exists(self.ARM_SN_PATH):
            path = self.ARM_SN_PATH
        elif os.path.exists(self.X86_SN_PATH):
            path = self.X86_SN_PATH
        if path is not None:
            with open(path, 'r') as file:
                return hashlib.sha1(file.read().rstrip('\0\n')).hexdigest()
        return None

    def _age(self):
        client = GConf.Client.get_default()
        age = client.get_int(self.AGE_PATH)
        if not age:
            return None
        return age

    def _gender(self):
        client = GConf.Client.get_default()
        return client.get_string(self.GENDER_PATH)

    def _activities(self):
        activities = {}
        entries, count = datastore.find(self._query())
        for entry in entries:
            activity_id = entry.metadata.get('activity', '')
            if activity_id not in activities:
                activities[activity_id] = []
            activities[activity_id].append(self._instance(entry))
        return activities

    def _query(self):
        query = {}
        query['timestamp'] = {}
        if self._start:
            query['timestamp']['start'] = self._start
        if self._end:
            query['timestamp']['end'] = self._end
        return query

    def _instance(self, entry):
        instance = []
        instance.append(entry.get_object_id())
        instance.append(_int(entry.metadata.get('filesize', None)))
        instance.append(_int(entry.metadata.get('creation_time', None)))
        instance.append(_int(entry.metadata.get('timestamp', None)))
        instance.append(self._buddies(entry))
        instance.append(None)
        instance.append(_bool(entry.metadata.get('share-scope', None)))
        instance.append(_bool(entry.metadata.get('title_set_by_user', None)))
        instance.append(_bool(entry.metadata.get('keep', None)))
        instance.append(_str(entry.metadata.get('mime_type', None)))
        instance.append(self._launches(entry))
        return instance

    def _buddies(self, entry):
        buddies = entry.metadata.get('buddies', None)
        if not buddies:
            return None
        return len(json.loads(buddies).values())

    def _launches(self, entry):
        launch_times = entry.metadata.get('launch-times', None)
        if not launch_times:
            return []
        return map(_int, launch_times.split(', '))


def _bool(value):
    if not value:
        return None
    if value == '1':
        return True
    return False


def _int(value):
    if not value:
        return None
    return int(value)


def _str(value):
    if not value:
        return None
    return str(value)
