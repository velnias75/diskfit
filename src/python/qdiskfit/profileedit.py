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

from .dialogs.nowhatsthisdlg import NoWhatsThisDialog
from .util.langcenv import LangCProcessEnvironment
from .models.targetmodel import TargetModel
from .dialogs.profile import Ui_ProfileEditor
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QHeaderView
from PyQt5.QtCore import QProcess
from PyQt5.QtCore import pyqtSlot
from .site import Site
import re


class ProfileEdit(NoWhatsThisDialog):

    __ui = None
    __tm = None
    __cp = ""

    __eject = QProcess()
    __dcdvd = QProcess()
    __dccdr = QProcess()
    __dccrx = re.compile("^\s+free_blocks = (\d+)$")
    __dcrex = re.compile("^ Free Blocks:\s+(\d+)\*(\d).*$")
    __direx = re.compile("^ Media ID:\s+(.*)$")

    def __init__(self, keyfile_, cur_):

        super(ProfileEdit, self).__init__()

        dc_env_ = LangCProcessEnvironment().env()

        self.__dcdvd.setProcessEnvironment(dc_env_)
        self.__dccdr.setProcessEnvironment(dc_env_)

        self.__ui = Ui_ProfileEditor()
        self.__ui.setupUi(self)

        self.__tm = TargetModel(self.__ui.table_targets, keyfile_)

        self.__ui.table_targets.setModel(self.__tm)
        self.__ui.table_targets.horizontalHeader(). \
            setSectionResizeMode(0, QHeaderView.Stretch)
        self.__ui.table_targets.horizontalHeader(). \
            setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.__ui.table_targets.horizontalHeader(). \
            setSectionResizeMode(2, QHeaderView.ResizeToContents)

        items_ = self.__tm.findItems(cur_)
        if len(items_):
            self.__ui.table_targets.selectRow(self.__tm.
                                              indexFromItem(items_[0]).row())

        self.__ui.button_add.clicked.connect(self.__tm.addTarget)
        self.__ui.button_remove.clicked.connect(self.__tm.removeTarget)
        self.__ui.button_detectCapacity.clicked.connect(self.detectCapacity)

        self.__ui.table_targets.selectionModel().selectionChanged. \
            connect(self.targetSelectionChanged)
        self.__tm.row_added.connect(self.__ui.table_targets.scrollToBottom)

    @pyqtSlot()
    def detectCapacity(self):
        if QMessageBox.Ok == QMessageBox. \
            information(None, self.tr("Detect capacity"),
                        self.tr("Please insert a blank DVD or CD "
                                "into the drive and wait until "
                                "it's loaded."),
                        QMessageBox.Ok | QMessageBox.Cancel):

            self.detectDVDCapacity()

    def detectCDCapacity(self):

        args_ = list()
        args_.append("-i")
        args_.append("-d")
        args_.append("/dev/cdrw")

        self.__cp = ""

        self.__dccdr.errorOccurred.connect(self.cd_error)
        self.__dccdr.readyReadStandardOutput.connect(self.cd_capacityAvailable)
        self.__dccdr.finished.connect(self.cd_finished)
        self.__dccdr.start(Site().get("cdrwtool", "cdrwtool"),
                           args_, QProcess.ReadOnly)
        self.__dccdr.waitForStarted()

    def detectDVDCapacity(self):

        arg_ = list()
        arg_.append("/dev/dvdrw")

        self.__cp = ""

        self.__dcdvd.errorOccurred.connect(self.dvd_error)
        self.__dcdvd.readyReadStandardOutput. \
            connect(self.dvd_capacityAvailable)
        self.__dcdvd.finished.connect(self.dvd_finished)
        self.__dcdvd.start(Site().get("mediainfo", "dvd+rw-mediainfo"),
                           arg_, QProcess.ReadOnly)
        self.__dcdvd.waitForStarted()

    @pyqtSlot(QProcess.ProcessError)
    def dvd_error(self, err):
        if err == QProcess.FailedToStart:
            QMessageBox.critical(None, self.tr("Error"),
                                 self.tr("Failed to launch {}.".
                                         format(Site().
                                                get("mediainfo",
                                                    "dvd+rw-mediainfo"))))
            self.dvd_finished(0, QProcess.NormalExit)

    @pyqtSlot(QProcess.ProcessError)
    def cd_error(self, err):
        if err == QProcess.FailedToStart:
            QMessageBox.critical(None, self.tr("Error"),
                                 self.tr("Failed to launch {}.".
                                         format(Site().
                                                get("cdrwtool", "cdrwtool"))))
            self.cd_finished(0, QProcess.NormalExit)

    @pyqtSlot()
    def dvd_capacityAvailable(self):
        self.__cp += self.__dcdvd.readAllStandardOutput().data(). \
            decode("utf-8")

    @pyqtSlot()
    def cd_capacityAvailable(self):
        self.__cp += self.__dccdr.readAllStandardOutput().data(). \
            decode("utf-8")

    @pyqtSlot(int, QProcess.ExitStatus)
    def cd_finished(self, ec, es):

        if not QProcess.CrashExit or ec == 0:

            if self.__dccdr.receivers(self.__dccdr.finished):
                self.__dccdr.finished.disconnect(self.cd_finished)

            cps_ = self.__cp.splitlines(False)
            mct_ = 0

            for str_ in cps_:
                c_match_ = self.__dccrx.search(str_)
                if c_match_:
                    mct_ = int(c_match_.group(1)) * 2048

            self.__tm.addTarget(self.tr("blankCD"), mct_, 2048)
            self.__ui.table_targets.resizeColumnToContents(1)

            self.__eject.start("eject")
        else:
            QMessageBox.critical(None, self.tr("Error"),
                                 self.tr("Could not detect capacity."))

        self.__cp = ""

    @pyqtSlot(int, QProcess.ExitStatus)
    def dvd_finished(self, ec, es):

        if not QProcess.CrashExit or ec == 0:

            if self.__dcdvd.receivers(self.__dcdvd.finished):
                self.__dcdvd.finished.disconnect(self.dvd_finished)

            cps_ = self.__cp.splitlines(False)
            mid_ = ""
            mct_ = 0
            mbs_ = 0

            for str_ in cps_:
                i_match_ = self.__direx.search(str_)
                c_match_ = self.__dcrex.search(str_)
                if i_match_:
                    mid_ = i_match_.group(1)
                elif c_match_:
                    mbs_ = int(c_match_.group(2)) * 1024
                    mct_ = int(c_match_.group(1)) * mbs_

            self.__tm.addTarget(mid_, mct_, mbs_)
            self.__ui.table_targets.resizeColumnToContents(1)

            self.__eject.start("eject")
        else:
            self.detectCDCapacity()

        self.__cp = ""

    @pyqtSlot()
    def targetSelectionChanged(self):
        self.__ui.button_remove.setEnabled(self.__ui.table_targets.
                                           selectionModel().hasSelection())

    @pyqtSlot()
    def accept(self):
        super(ProfileEdit, self).accept()
        self.__tm.saveRC()

# kate: indent-mode: python
