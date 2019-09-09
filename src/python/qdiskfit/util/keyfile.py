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

from PyQt5.QtCore import qDebug
from gi.repository import GLib
from ..site import Site
import os


class Keyfile:

    __instance = None

    class __Keyfile:

        __rc = GLib.KeyFile.new()

        def __init__(self):

            sd_ = ["./",
                   os.environ["HOME"] + "/",
                   Site().get("sysconfdir", "/etc/")
                   ]

            rc_fp_ = None

            try:
                rc_fp_ = self.__rc.load_from_dirs(".diskfitrc", sd_,
                                                  GLib.KeyFileFlags.NONE). \
                    full_path
            except GLib.Error as e1:

                qDebug(e1.message.encode())

                try:
                    rc_fp_ = self.__rc.load_from_dirs("diskfitrc", sd_,
                                                      GLib.KeyFileFlags.NONE). \
                        full_path
                except GLib.Error as e2:
                    qDebug(e2.message.encode())

            if rc_fp_ is not None:
                qDebug("Key file loaded from: " + rc_fp_)
            else:
                qDebug("No key file found")

        def getTargetsize(self, target_):
            try:
                return int(self.__rc.get_value(target_, "size"))
            except GLib.Error:
                return None

        def getBlocksize(self, target_):
            try:
                return int(self.__rc.get_value(target_, "bs"))
            except GLib.Error:
                return 0

        def get_groups(self):
            return self.__rc.get_groups()

        def get_keys(self, grp_):
            return self.__rc.get_keys(grp_)

        def get_value(self, grp_, key_):
            return self.__rc.get_value(grp_, key_)

        def remove_group(self, grp_):
            self.__rc.remove_group(grp_)

        def set_comment(self, grp_, key_, comment_):
            self.__rc.set_comment(grp_, key_, comment_)

        def set_uint64(self, grp_, key_, value_):
            self.__rc.set_uint64(grp_, key_, value_)

        def addTarget(self, name_, size_, bs_):
            self.__rc.set_uint64(name_, "size", size_)
            self.__rc.set_uint64(name_, "bs", bs_)

        def save_to_file(self, filename_):
            self.__rc.save_to_file(filename_)

    def __new__(cls):
        if not Keyfile.__instance:
            Keyfile.__instance = Keyfile.__Keyfile()
        return Keyfile.__instance

    def __getattr__(self, atname_):
        return getattr(self.__instance, atname_)

# kate: indent-mode: python
