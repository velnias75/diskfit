# -*- coding: utf-8 -*-
#
# Copyright 2019 by Heiko Schäfer <heiko@rangun.de>
#
# This file is part of DiskFit.
#
# DiskFit is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# DiskFit is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with DiskFit.  If not, see <http://www.gnu.org/licenses/>.
#

from .dialogs.profile import Ui_ProfileEditor
from PyQt5.QtWidgets import QDialog
from gi.repository import GLib
from .site import Site
import os


class ProfileEdit(QDialog):

    __ui = None
    __rc = GLib.KeyFile.new()

    def __init__(self):

        super(ProfileEdit, self).__init__()

        self.__ui = Ui_ProfileEditor()
        self.__ui.setupUi(self)

        sd_ = ["./",
               os.environ["HOME"] + "/",
               Site().get("sysconfdir", "/etc/diskfit"),
               None
               ]

        has_rc_ = (self.__rc.
                   load_from_dirs(".diskfitrc", sd_, GLib.KeyFileFlags.NONE) or
                   self.__rc.
                   load_from_dirs("diskfitrc", sd_, GLib.KeyFileFlags.NONE))
