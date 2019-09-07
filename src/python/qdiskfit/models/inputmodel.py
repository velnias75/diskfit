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
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtCore import QModelIndex
from PyQt5.QtCore import QSettings
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import qDebug
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFileDialog
from .modelitems.hrfileitem import HRFileItem
from .modelitems.iconfileitem import IconFileItem
from ..util.hrsize import HRSize
from .targetsizemodel import TargetSizeModel


class InputModel(TargetSizeModel):

    __par = None
    __sta = None
    __asa = None
    __aca = None
    __bca = None

    def __init__(self, parent_, start_, selAllAct_, clearAllAct_,
                 clearAllBut_, oversizeCheck=True):

        super(InputModel, self).__init__(oversizeCheck)

        self.setHorizontalHeaderLabels([
            QCoreApplication.translate("InputModel", "File"),
            QCoreApplication.translate("InputModel", "Size")])

        self.__sta = start_
        self.__par = parent_
        self.__asa = selAllAct_
        self.__aca = clearAllAct_
        self.__bca = clearAllBut_

        self.rowsInserted.connect(self.disableOversizeItems)
        self.rowsInserted.connect(self.modelChanged)
        self.rowsRemoved.connect(self.modelChanged)

        self.modelChanged()

    def sort(self, col, order):

        l_ = list()

        while self.rowCount() > 0:
            s_ = self.__par.selectionModel().isRowSelected(0, QModelIndex())
            r_ = self.takeRow(0)
            l_.append((r_[0], r_[1], s_))

        if col == 0:
            l_.sort(key=lambda name: name[0].name() + "|" + name[0].path(),
                    reverse=(order == Qt.DescendingOrder))
        else:
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
            if self.item(i).isEnabled():
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

        anyEnabled_ = False

        for r in range(0, len_):
            tot_ += self.item(r, 1).num()
            if self.item(r, 1).isEnabled():
                anyEnabled_ = True

        if len_ > 0:
            self.__par.setSummary(QCoreApplication.
                                  translate("InputModel", "{0} in {1} files").
                                  format(HRSize.sizeString(tot_), str(len_)))
        else:
            self.__par.setSummary(QCoreApplication.
                                  translate("InputModel", "No files"))

        self.__par.header().setSortIndicatorShown(len_ > 0)

        if self.__sta is not None:
            self.__sta.setEnabled(anyEnabled_ and len_ > 0)

        if self.__asa is not None:
            self.__asa.setEnabled(len_ > 0)

        if self.__aca is not None:
            self.__aca.setEnabled(len_ > 0)

        if self.__bca is not None:
            self.__bca.setEnabled(len_ > 0)

    def columns(self):
        return (1, 0, 1)

    @pyqtSlot(float)
    def setTargetSize(self, target_):
        super(InputModel, self).setTargetSize(target_)
        self.modelChanged()

    @pyqtSlot()
    def addFiles(self):

        settings = QSettings()

        fdlg_ = QFileDialog()

        state_ = settings.value("inputFDlgState")
        if state_ is not None:
            fdlg_.restoreState(state_)

        geomy_ = settings.value("inputFDlgGeometry")
        if geomy_ is not None:
            fdlg_.restoreGeometry(geomy_)

        fdlg_.setDirectory(settings.value("inputDir"))
        fdlg_.setFileMode(QFileDialog.ExistingFiles)
        fdlg_.setNameFilters((self.tr("Any files (*)"),
                              self.tr("Video files (*.mp4 *.mpg *.m3u8 *.ts "
                                      "*.avi *.wmv *.flv *.webm *.ogv *.vob "
                                      "*.mpeg)"),
                              self.tr("Audio files (*.mp3 *.wav *.ogg "
                                      "*.wma *.au)"),
                              self.tr("Image files (*.png *.xpm *.jpg "
                                      "*.gif *.svg *.svgz)")))
        fdlg_.exec_()

        settings.setValue("inputFDlgGeometry", fdlg_.saveGeometry())
        settings.setValue("inputFDlgState", fdlg_.saveState())
        settings.setValue("inputDir", fdlg_.directory().absolutePath())

        self.addFileList(fdlg_.selectedFiles())

        self.__par.header().setSortIndicatorShown(False)

    def getAccuSize(self, items_, bs_):

        accu_ = 0

        for i_ in items_:
            if i_.column() == 1:
                if bs_ > 0:
                    padded_size_ = self.itemFromIndex(i_).num() + \
                        (bs_ - (self.itemFromIndex(i_).num() & (bs_ - 1)))
                else:
                    padded_size_ = self.itemFromIndex(i_).num()

                if self.itemFromIndex(i_).isEnabled():
                    accu_ += padded_size_

        return accu_

    def addFileList(self, files_):
        for file_ in files_:
            ifi_ = IconFileItem(file_)
            if not len(self.findItems(ifi_.text())):
                self.appendRow((ifi_, HRFileItem(file_)))

    @pyqtSlot()
    def removeAll(self):
        self.removeRows(0, self.rowCount())

    @pyqtSlot()
    def removeFiles(self):
        while len(self.__par.selectionModel().selectedIndexes()):
            self.removeRow(self.__par.selectionModel().
                           selectedIndexes()[0].row())

# kate: indent-mode: python
