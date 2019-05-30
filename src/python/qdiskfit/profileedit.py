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

from .models.targetmodel import TargetModel
from .dialogs.profile import Ui_ProfileEditor
from PyQt5.QtWidgets import QHeaderView
from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import pyqtSlot


class ProfileEdit(QDialog):

    __ui = None
    __tm = None

    def __init__(self):

        super(ProfileEdit, self).__init__()

        self.__ui = Ui_ProfileEditor()
        self.__ui.setupUi(self)

        self.__tm = TargetModel(self.__ui.table_targets)

        self.__ui.table_targets.setModel(self.__tm)
        self.__ui.table_targets.horizontalHeader(). \
            setSectionResizeMode(0, QHeaderView.Stretch)
        self.__ui.table_targets.horizontalHeader(). \
            setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.__ui.table_targets.horizontalHeader(). \
            setSectionResizeMode(2, QHeaderView.ResizeToContents)

        self.__ui.button_add.clicked.connect(self.__tm.addTarget)
        self.__ui.button_remove.clicked.connect(self.__tm.removeTarget)

        self.__ui.table_targets.selectionModel().selectionChanged. \
            connect(self.targetSelectionChanged)
        self.__tm.row_added.connect(self.__ui.table_targets.scrollToBottom)

    @pyqtSlot()
    def targetSelectionChanged(self):
        self.__ui.button_remove.setEnabled(self.__ui.table_targets.
                                           selectionModel().hasSelection())

    @pyqtSlot()
    def accept(self):
        super(ProfileEdit, self).accept()
        self.__tm.saveRC()

# kate: indent-mode: python
