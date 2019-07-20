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

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import QPoint
from PyQt5.QtWidgets import QHeaderView
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QMenu
from .mainwindow.inputwidget import Ui_inputWidget


class InputWidget(QWidget):

    __ui = None
    __ctxMenuActions = None

    def __init__(self, parent=None, drop_=True):
        super(InputWidget, self).__init__(parent)

        self.__ui = Ui_inputWidget()
        self.__ui.setupUi(self)

        self.__ui.table_input.setAcceptDrops(drop_)
        self.__ui.table_input.setDragEnabled(not drop_)

        self.__ui.table_input. \
            customContextMenuRequested.connect(self.inputContextRequested)

    def setTableToolTip(self, tt_):
        self.__ui.table_input.setToolTip(tt_)

    def summary(self):
        return self.__ui.label_inputSummary.text()

    def setSummary(self, txt_):
        return self.__ui.label_inputSummary.setText(txt_)

    def header(self):
        return self.__ui.table_input.header()

    def selectionModel(self):
        return self.__ui.table_input.selectionModel()

    def selectedIndexes(self):
        return self.__ui.table_input.selectedIndexes()

    def model(self):
        return self.__ui.table_input.model()

    def setModel(self, model_):
        self.__ui.table_input.setModel(model_)
        self.__ui.table_input.header(). \
            setSectionResizeMode(0, QHeaderView.Stretch)
        self.__ui.table_input.header(). \
            setSectionResizeMode(1, QHeaderView.ResizeToContents)

    def setContextMenuActions(self, acts_):
        self.__ctxMenuActions = acts_

    @pyqtSlot(QPoint)
    def inputContextRequested(self, pos):

        if self.__ctxMenuActions is not None:
            globalPos = self.__ui.table_input.mapToGlobal(pos)

            menu_ = QMenu()

            for a_ in self.__ctxMenuActions:
                if a_ is not None:
                    menu_.addAction(a_)
                else:
                    menu_.addSeparator()

            menu_.exec_(globalPos)

# kate: indent-mode: python
