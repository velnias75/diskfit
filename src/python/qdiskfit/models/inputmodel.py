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

from PyQt5.QtCore import QItemSelectionModel
from PyQt5.QtCore import QModelIndex
from PyQt5.QtCore import QSettings
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import qDebug
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtWidgets import QFileDialog
from .modelitems.hrfileitem import HRFileItem
from .modelitems.iconfileitem import IconFileItem
from .modelitems.hrsize import HRSize


class InputModel(QStandardItemModel, HRSize):

    __par = None
    __sum = None
    __sta = None
    __asa = None
    __aca = None
    __bca = None

    def __init__(self, parent_, summary_, start_, selAllAct_, clearAllAct_,
                 clearAllBut_):

        super(InputModel, self).__init__()

        self.setHorizontalHeaderLabels([
            self.tr("File", "InputModel"),
            self.tr("Size", "InputModel")])

        self.__sum = summary_
        self.__sta = start_
        self.__par = parent_
        self.__asa = selAllAct_
        self.__aca = clearAllAct_
        self.__bca = clearAllBut_

        self.rowsInserted.connect(self.modelChanged)
        self.rowsRemoved.connect(self.modelChanged)

    def sort(self, col, order):
        if col == 0:
            super().sort(col, order)
        else:

            l_ = list()

            while self.rowCount() > 0:
                s_ = self.__par.selectionModel().isRowSelected(0,
                                                               QModelIndex())
                r_ = self.takeRow(0)
                l_.append((r_[0], r_[1], s_))

            l_.sort(key=lambda size: size[1].num(),
                    reverse=(order == Qt.DescendingOrder))

            for row in l_:
                self.appendRow((row[0], row[1]))
                if row[2]:
                    self.__par.selectionModel(). \
                        select(row[0].index(), QItemSelectionModel.Select)
                    self.__par.selectionModel(). \
                        select(row[1].index(), QItemSelectionModel.Select)

    def files(self):

        files_ = list()

        for i in range(0, self.rowCount()):
            files_.append(self.item(i))

        return files_

    def canDropMimeData(self, data, action, row, column, parent):
        if data.hasFormat("text/uri-list"):
            return True
        return False

    def dropMimeData(self, data, action, row, column, parent):

        if not self.canDropMimeData(data, action, row, column, parent):
            return False

        if data.hasUrls():

            files_ = list()

            for url_ in data.urls():
                if url_.isLocalFile():
                    files_.append(url_.toLocalFile())

            self.addFileList(files_)

        return True

    @pyqtSlot()
    def modelChanged(self):

        tot_ = 0
        len_ = self.rowCount()

        for r in range(0, len_):
            tot_ += self.item(r, 1).num()

        if len_ > 0:
            self.__sum.setText(self.sizeString(tot_) +
                               self.tr(" in ", "InputModel") +
                               str(len_) + self.tr(" files", "InputModel"))
        else:
            self.__sum.setText(self.tr("No files", "InputModel"))

        self.__par.header().setSortIndicatorShown(len_ > 0)
        self.__sta.setEnabled(len_ > 0)
        self.__asa.setEnabled(len_ > 0)
        self.__aca.setEnabled(len_ > 0)
        self.__bca.setEnabled(len_ > 0)

    @pyqtSlot()
    def addFiles(self):

        settings = QSettings()

        self.__par.header().setSortIndicatorShown(False)

        fdlg_ = QFileDialog()

        state_ = settings.value("inputFDlgState")
        if state_ is not None:
            fdlg_.restoreState(state_)

        geomy_ = settings.value("inputFDlgGeometry")
        if geomy_ is not None:
            fdlg_.restoreGeometry(geomy_)

        filtr_ = settings.value("inputFilters")
        if filtr_ is not None:
            fdlg_.setNameFilters(filtr_)

        fdlg_.setDirectory(settings.value("inputDir"))
        fdlg_.setFileMode(QFileDialog.ExistingFiles)

        fdlg_.exec_()

        settings.setValue("inputFDlgGeometry", fdlg_.saveGeometry())
        settings.setValue("inputFDlgState", fdlg_.saveState())
        settings.setValue("inputFilters", fdlg_.nameFilters())
        settings.setValue("inputDir", fdlg_.directory().absolutePath())

        self.addFileList(fdlg_.selectedFiles())

    def addFileList(self, files_):
        for file_ in files_:
            self.appendRow((IconFileItem(file_), HRFileItem(file_)))

    @pyqtSlot()
    def removeAll(self):
        self.removeRows(0, self.rowCount())

    @pyqtSlot()
    def removeFiles(self):
        while len(self.__par.selectionModel().selectedIndexes()):
            self.removeRow(self.__par.selectionModel().
                           selectedIndexes()[0].row())
