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

import dbus

from gi.repository import GLib

from jarabe.webservice import account
from jarabe.webservice import accountsmanager


class Account(account.Account):

    DBUS_COLLECT_SIGNAL = 'Collect'
    DBUS_HARVEST_IFACE = 'org.sugarlabs.Harvest'
    DBUS_HARVEST_PATH = '/org/sugarlabs/Havest'

    def __init__(self):
        bus = dbus.SystemBus()
        bus.add_signal_receiver(self.__collect_cb,
                                self.DBUS_COLLECT_SIGNAL,
                                self.DBUS_HARVEST_IFACE)
        GLib.idle_add(self.__collect_cb)

    def __collect_cb(self):
        service = accountsmanager.get_service('harvest')
        try:
            service.Harvest().collect()
        except Exception:
            pass

    def get_token_state(self):
        return self.STATE_VALID


def get_account():
    return Account()
