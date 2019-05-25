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

from PyQt5.QtCore import QUrl
from PyQt5.QtCore import qDebug
from PyQt5.QtCore import QMimeData
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QStandardItemModel
from .modelitems.iconfileitem import IconFileItem
from .modelitems.echotooltipitem import EchoTooltipItem
from .modelitems.multifiledragitem import MultiFileDragItem
import re


class OutputModel(QStandardItemModel):

    modelSaveable = pyqtSignal(bool)

    __par = None
    __sum = None
    __hdr = None
    __imd = None
    __rex = re.compile("'([^']+)'")

    def __init__(self, parent_, summary_, in_model_):

        super(OutputModel, self).__init__()

        self.__hdr = [
            self.tr("Files", "OutputModel"),
            self.tr("Count", "OutputModel"),
            self.tr("Size", "OutputModel"),
            self.tr("Percentage", "OutputModel")]

        self.setHorizontalHeaderLabels(self.__hdr)

        self.__par = parent_
        self.__sum = summary_
        self.__imd = in_model_

    def setLastResult(self, result_):

        self.removeRows(0, self.rowCount())

        for r_ in result_:

            fa_ = self.__rex.findall(r_[0])

            l_ = (MultiFileDragItem(fa_),
                  EchoTooltipItem(r_[1], True),
                  EchoTooltipItem(r_[2], True),
                  EchoTooltipItem(r_[3], True))

            ts_ = 0
            for ma_ in fa_:
                ts_ += self.__imd.item(self.__imd.
                                       indexFromItem(self.__imd.
                                                     findItems(ma_)[0]).row(),
                                       1).num()

            for i_, ma_ in enumerate(fa_):

                item_ = self.__imd.item(self.__imd.
                                        indexFromItem(self.__imd.
                                                      findItems(ma_)[0]).row(),
                                        1)

                rsit_ = EchoTooltipItem(item_.relativeSizePctString(ts_))
                rsit_.setToolTip(rsit_.text() + self.tr(" of ", "OutputModel")
                                 + r_[2])

                l_[0].setChild(i_, 0, IconFileItem(ma_))
                l_[0].setChild(i_, 1, EchoTooltipItem("1"))
                l_[0].setChild(i_, 2, EchoTooltipItem(item_.text()))
                l_[0].setChild(i_, 3, rsit_)

            self.appendRow(l_)

        self.__par.scrollToBottom()
        self.__sum.setText(str(self.rowCount()) +
                           self.tr(" results found", "OutputModel"))

        self.modelSaveable.emit(self.rowCount() > 0)

    @pyqtSlot()
    def saveModel(self):

        f_ = None

        try:
            f_ = open(QFileDialog.getSaveFileName(None, self.tr("Save result"),
                                                  "qdiskfit.txt")[0], "wt")
            for r_ in range(0, self.rowCount()):
                f_.write("[ ")
                for fi_ in self.item(r_, 0).files():
                    f_.write("\'" + fi_ + "\' ")
                f_.write("]:" + self.item(r_, 1).text() + " = " +
                         self.item(r_, 2).text() + " (" +
                         self.item(r_, 3).text() + ")\n")
        except OSError as e:
            QMessageBox.critical(None, self.tr("Error saving result"),
                                 "\'" + e.filename + "\': " +
                                 e.strerror + " (" + str(e.errno) + ")")
        finally:
            try:
                if f_ is not None:
                    f_.close()
            except OSError:
                pass

    def mimeTypes(self):
        return list("text/uri-list")

    def mimeData(self, indexes):

        urls_ = list()
        mime_ = QMimeData()

        for idx in indexes:
            if idx.column() == 0:
                for file in self.item(idx.row(), 0).files():
                    urls_.append(QUrl("file://" + file))

        mime_.setUrls(urls_)

        return mime_
