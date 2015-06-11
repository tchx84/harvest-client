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
import re
import json
import hashlib
import subprocess

from gi.repository import GConf

from sugar3.datastore import datastore


class CropErrorNotReady:
    pass


class Crop(object):

    VERSION = '000501'

    ARM_SN_PATH = '/ofw/serial-number/serial-number'
    X86_SN_PATH = '/proc/device-tree/serial-number'
    AGE_PATH = '/desktop/sugar/user/birth_timestamp'
    GENDER_PATH = '/desktop/sugar/user/gender'
    BUILD_PATH = '/boot/olpc_build'
    UPDATED_PATH = '/var/lib/misc/last_os_update.stamp'

    SS_REPONAME_PATH = '/desktop/sugar/collaboration/harvest_reponame'
    SS_RE = '@%s(\s*)(\d+):(\w+)'
    SS_CMD = 'su --session-command "/usr/bin/yum -C version installed -v"'

    def __init__(self, start=None, end=None, collect_extras=False):
        self._start = start
        self._end = end
        self._data = None
        self._collect_extras = collect_extras

    def serialize(self):
        if not self._data:
            raise CropErrorNotReady()
        return json.dumps(self._data)

    def grown(self):
        if not self._data:
            raise CropErrorNotReady()
        if not self._data[2].keys():
            return False
        return True

    def characterizable(self):
        """ check if all learner characteristics are available """
        if self._serial_number() is None or \
           self._grouping() is None or \
           self._gender() is None:
            return False
        return True

    def collect(self):
        self._data = []
        self._data.append(self._laptop())
        self._data.append(self._learner())
        activities, extras = self._activities()
        self._data.append(activities)
        self._data.append(self._counters())
        self._data.append(extras)

    def _laptop(self):
        laptop = []
        laptop.append(self._serial_number())
        laptop.append(self._build())
        laptop.append(self._snapshot())
        laptop.append(self._updated())
        laptop.append(self._collected())
        return laptop

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

    def _build(self):
        if os.path.exists(self.BUILD_PATH):
            with open(self.BUILD_PATH, 'r') as file:
                return file.read().rstrip('\0\n')
        return None

    def _snapshot(self):
        client = GConf.Client.get_default()
        reponame = client.get_string(self.SS_REPONAME_PATH)

        if not reponame:
            return None

        try:
            raw = subprocess.check_output(self.SS_CMD, shell=True)
            match = re.search(self.SS_RE % reponame, raw)
            return match.groups(0)[2]
        except:
            return None

    def _updated(self):
        if os.path.exists(self.UPDATED_PATH):
            return int(os.stat(self.UPDATED_PATH).st_mtime)
        return None

    def _collected(self):
        return self._end

    def _learner(self):
        learner = []
        learner.append(0)
        learner.append(self._gender())
        learner.append(self._grouping())
        return learner

    def _age(self):
        client = GConf.Client.get_default()
        age = client.get_int(self.AGE_PATH)
        if not age:
            return None
        return age

    def _gender(self):
        client = GConf.Client.get_default()
        return client.get_string(self.GENDER_PATH)

    def _grouping(self):
        try:
            from jarabe.intro.agepicker import calculate_age
            from jarabe.intro.agepicker import age_to_group_label

            age = calculate_age(self._age())
            return age_to_group_label(age)
        except:
            return ''

    def _activities(self):
        activities = {}
        extras = {}
        entries, count = datastore.find(self._query())
        for entry in entries:
            activity_id = entry.metadata.get('activity', '')
            if activity_id not in activities:
                activities[activity_id] = []
            activities[activity_id].append(self._instance(entry))
            if self._collect_extras:
                if activity_id not in extras:
                    extras[activity_id] = []
                extras[activity_id].append(self._extras(entry))
        return activities, extras

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
        instance.append(_bool(entry.metadata.get('share-scope', None)))
        instance.append(_bool(entry.metadata.get('title_set_by_user', None)))
        instance.append(_bool(entry.metadata.get('keep', None)))
        instance.append(_str(entry.metadata.get('mime_type', None)))
        instance.append(self._times(entry))
        return instance

    def _extras(self, entry):
        # collect extra metadata saved by the activities
        # these fields are already collected, or are big and not useful like
        # the preview. 'cover_image' is used by GetBooks activity
        excluded = [
            'filesize', 'creation_time', 'timestamp', 'share-scope', 'keep',
            'title_set_by_user', 'mime_type', 'buddies', 'launch-times',
            'spent-times', 'activity', 'object_id', 'icon-color', 'mtime',
            'preview', 'cover_image']
        extras = {}
        extras['object_id'] = entry.get_object_id()
        for field in entry.metadata.keys():
            if field not in excluded:
                extras[field] = entry.metadata.get(field)
        return extras

    def _buddies(self, entry):
        buddies = entry.metadata.get('buddies', None)
        if not buddies:
            return None
        return len(json.loads(buddies).values())

    def _times(self, entry):
        launch_times = entry.metadata.get('launch-times', None)
        if not launch_times:
            return []
        else:
            launch_times = map(_int, launch_times.split(', '))

        spent_times = entry.metadata.get('spent-times', None)
        if not spent_times:
            spent_times = [None for launch in launch_times]
        else:
            spent_times = map(_int, spent_times.split(', '))

        return zip(launch_times, spent_times)

    def _counters(self):
        try:
            import imp
            import time
            from datetime import datetime

            path = '/opt/harvest-monitor/harvest/log.py'
            module = imp.load_source('', path)
            log = module.Log()

            start_date = datetime.fromtimestamp(self._start or 0)
            start = int(time.mktime(start_date.date().timetuple()))

            counters = []
            for entry in log.find(start, self._end):
                counters.append(entry)
        except:
            counters = []

        return counters


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
