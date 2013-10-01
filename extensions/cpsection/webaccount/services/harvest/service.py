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

from gettext import gettext as _

from gi.repository import GConf
from gi.repository import Gtk
from gi.repository import GLib

from sugar3.graphics import style
from jarabe.webservice import accountsmanager
from cpsection.webaccount.web_service import WebService


class WebService(WebService):

    def __init__(self):
        self._service = accountsmanager.get_service('harvest')

    def get_icon_name(self):
        return 'activity-journal'

    def config_service_cb(self, widget, event, container):
        workspace = Gtk.VBox()
        workspace.set_border_width(style.DEFAULT_SPACING * 2)

        separator = Gtk.HSeparator()
        workspace.pack_start(separator, False, True, 0)

        title_label = Gtk.Label(_('Harvest'))
        title_label.set_alignment(0, 0)
        workspace.pack_start(title_label, False, True, 0)

        label_group = Gtk.SizeGroup(Gtk.SizeGroupMode.HORIZONTAL)
        entry_group = Gtk.SizeGroup(Gtk.SizeGroupMode.HORIZONTAL)
        form = Gtk.VBox(spacing=style.DEFAULT_SPACING)
        form.set_border_width(style.DEFAULT_SPACING * 2)
        workspace.pack_start(form, True, False, 0)

        description = _('This extension goal is to make learning visible to '
                        'educators and decision makers.')
        desc_label = Gtk.Label(description)
        desc_label.set_line_wrap(True)
        desc_label.set_alignment(0, 0)
        form.pack_start(desc_label, True, False, 0)

        host_field = AutoField(_('Hostname'), self._service.Harvest.HOSTNAME)
        label_group.add_widget(host_field.label)
        entry_group.add_widget(host_field.entry)
        form.pack_start(host_field, False, True, 0)

        key_field = AutoField(_('API Key'), self._service.Harvest.API_KEY)
        key_field.entry.set_visibility(False)
        label_group.add_widget(key_field.label)
        entry_group.add_widget(key_field.entry)
        form.pack_start(key_field, False, True, 0)

        options = [[_('Weekly'), self._service.Harvest.WEEKLY],
                   [_('Monthly'), self._service.Harvest.MONTHLY]]
        frequency_field = ComboField(_('Frequency'), options,
                                     self._service.Harvest.FREQUENCY)
        label_group.add_widget(frequency_field.label)
        entry_group.add_widget(frequency_field.combo)
        form.pack_start(frequency_field, False, True, 0)

        collect_form = Gtk.VBox(spacing=style.DEFAULT_SPACING)
        collect_form.set_border_width(style.DEFAULT_SPACING * 2)
        workspace.pack_start(collect_form, True, False, 0)

        instructions = _('After completing the harvest server information, '
                         'please click on collect button.')
        inst_label = Gtk.Label(instructions)
        inst_label.set_line_wrap(True)
        inst_label.set_alignment(0, 0)
        collect_form.pack_start(inst_label, True, False, 0)

        collect_field = CollectButtonField(self._service.Harvest)
        collect_form.pack_start(collect_field, False, True, 0)

        for c in container.get_children():
            container.remove(c)

        container.pack_start(workspace, False, False, 0)
        container.show_all()


class CollectButtonField(Gtk.HBox):
    __gtype_name__ = 'SugarCollectButtonField'

    def __init__(self, harvest):
        Gtk.HBox.__init__(self, spacing=style.DEFAULT_SPACING)
        self._harvest = harvest

        self.button = Gtk.Button(_('Collect'))
        self.button.set_alignment(1, 0.5)
        self.pack_start(self.button, False, True, 0)

        self.label = Gtk.Label('')
        self.label.modify_fg(Gtk.StateType.NORMAL,
                             style.COLOR_SELECTION_GREY.get_gdk_color())
        self.pack_start(self.label, False, True, 0)

        self.button.connect('clicked', self.__collect_cb)

    def __collect_cb(self, button, data=None):
        self.label.set_text(_('Please wait...'))
        GLib.idle_add(self.__do_collect_cb)

    def __do_collect_cb(self):
        result = self._harvest().collect()
        if result == self._harvest.TOO_SOON:
            self.label.set_text(_('Too soon to collect again.'))
        elif result == self._harvest.NOTHING:
            self.label.set_text(_('Nothing new to collect.'))
        elif result == self._harvest.OK:
            self.label.set_text(_('Successfully collected.'))
        else:
            self.label.set_text(_('Could not be collected.'))


class ComboField(Gtk.HBox):
    __gtype_name__ = 'SugarComboField'

    TEXT = 0
    VALUE = 1

    def __init__(self, label_text, options, path):
        Gtk.HBox.__init__(self, spacing=style.DEFAULT_SPACING)
        self._options = options
        self._path = path

        self.label = Gtk.Label(label_text)
        self.label.modify_fg(Gtk.StateType.NORMAL,
                             style.COLOR_SELECTION_GREY.get_gdk_color())
        self.label.set_alignment(1, 0.5)
        self.pack_start(self.label, False, True, 0)

        self.combo = Gtk.ComboBoxText()
        for option in self._options:
            self.combo.append_text(option[self.TEXT])
        self.combo.set_active(0)
        self.pack_start(self.combo, False, True, 0)
        self._restore_option()
        self.combo.connect('changed', self.__changed_cb)

    def __changed_cb(self, combo):
        client = GConf.Client.get_default()
        index = combo.get_active()
        client.set_int(self._path, self._options[index][self.VALUE])

    def _restore_option(self):
        client = GConf.Client.get_default()
        value = client.get_int(self._path)
        for index, option in enumerate(self._options):
            if value == option[self.VALUE]:
                self.combo.set_active(index)


class AutoField(Gtk.HBox):
    __gtype_name__ = 'SugarAutoField'

    def __init__(self, label_text, path):
        Gtk.HBox.__init__(self, spacing=style.DEFAULT_SPACING)

        self.label = Gtk.Label(label_text)
        self.label.modify_fg(Gtk.StateType.NORMAL,
                             style.COLOR_SELECTION_GREY.get_gdk_color())
        self.label.set_alignment(1, 0.5)
        self.pack_start(self.label, False, True, 0)

        self.entry = AutoEntry(path)
        self.entry.set_max_length(50)
        self.entry.set_width_chars(50)
        self.pack_start(self.entry, False, True, 0)


class AutoEntry(Gtk.Entry):
    __gtype_name__ = 'SugarAutoEntry'

    DELAY = 1

    def __init__(self, path):
        Gtk.Entry.__init__(self)
        self._path = path
        self._timeout_id = None
        self._restore_text()
        self.connect('key-press-event', self.__pressed_start_cb)

    def _restore_text(self):
        client = GConf.Client.get_default()
        text = client.get_string(self._path)
        if text is not None:
            self.set_text(text)

    def __save_text_cb(self):
        client = GConf.Client.get_default()
        client.set_string(self._path, self.get_text())
        self._timeout_id = None
        return False

    def __pressed_start_cb(self, entry, data=None):
        if self._timeout_id is not None:
            GLib.source_remove(self._timeout_id)
        self._timeout_id = GLib.timeout_add_seconds(self.DELAY,
                                                    self.__save_text_cb)


def get_service():
    return WebService()
