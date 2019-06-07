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

from .modelitems.targetnameitem import TargetNameItem
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtCore import QCoreApplication
from .modelitems.sizeitem import SizeItem
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import qDebug
from gi.repository import GLib
from ..site import Site
import os


class TargetModel(QStandardItemModel):

    rc_changed = pyqtSignal()
    row_added = pyqtSignal()

    __rc = GLib.KeyFile.new()
    __par = None

    def __init__(self, parent_):

        super(TargetModel, self).__init__()

        self.__par = parent_

        sd_ = ["./",
               os.environ["HOME"] + "/",
               Site().get("sysconfdir", "/etc/"),
               None
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

        self.setHorizontalHeaderLabels([
            self.tr("Target"),
            self.tr("Total size"),
            self.tr("Block size")])

        for grp_ in self.__rc.get_groups()[0]:

            grp_item_ = TargetNameItem(grp_, self)
            size_item_ = SizeItem(0)
            bs_item_ = SizeItem(2048, True)

            for key_ in self.__rc.get_keys(grp_)[0]:
                if key_ == "size":
                    size_item_.setData(int(self.__rc.get_value(grp_, key_)))
                if key_ == "bs":
                    bs_item_.setData(int(self.__rc.get_value(grp_, key_)))

            self.appendRow((grp_item_, size_item_, bs_item_))

    @pyqtSlot()
    def addTarget(self, name_="", total_=0, bs_=2048):
        self.appendRow((TargetNameItem(name_, self, False),
                        SizeItem(total_),
                        SizeItem(bs_)))

        self.row_added.emit()

    @pyqtSlot()
    def removeTarget(self):
        r_ = self.takeRow(self.__par.selectionModel().
                          selectedIndexes()[0].row())
        try:
            self.__rc.remove_group(r_[0].text())
        except GLib.Error:
            pass

        self.__par.selectionModel().clearSelection()

    @pyqtSlot()
    def saveRC(self):
        self.__rc.set_comment(None, None,
                              " Created by " +
                              QCoreApplication.applicationName() + "/" +
                              QCoreApplication.applicationVersion())

        for r_ in range(0, self.rowCount()):
            if self.item(r_, 0).isValid() and \
               self.item(r_, 1).isValid() and \
               self.item(r_, 2).isValid():
                grp_ = self.item(r_, 0).text()
                self.__rc.set_uint64(grp_, "size",
                                     int(self.item(r_, 1).data()))
                self.__rc.set_uint64(grp_, "bs",
                                     int(self.item(r_, 2).data()))

        try:
            self.__rc.save_to_file(os.environ["HOME"] + "/.diskfitrc")
            self.rc_changed.emit()
        except GLib.Error as e:
            QMessageBox.critical(None, self.tr("Error"), e.message)

    def getBlocksize(self, target_):
        try:
            return int(self.__rc.get_value(target_, "bs"))
        except GLib.Error:
            return 0

# kate: indent-mode: python
