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

from PyQt5.QtCore import Qt
from PyQt5.QtCore import QUrl
from PyQt5.QtCore import qDebug
from PyQt5.QtCore import QFileInfo
from PyQt5.QtCore import QSettings
from PyQt5.QtCore import QMimeData
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QStandardItemModel
from .modelitems.iconfileitem import IconFileItem
from .modelitems.outputsizeitem import OutputSizeItem
from .modelitems.echotooltipitem import EchoTooltipItem
from .modelitems.leftoveritem import LeftOverItem
from .modelitems.multifiledragitem import MultiFileDragItem
from .targetsizemodel import TargetSizeModel


class OutputModel(TargetSizeModel):

    modelSaveable = pyqtSignal(bool)
    resultReady = pyqtSignal()

    __par = None
    __sum = None
    __hdr = None
    __imd = None

    __result = None

    def __init__(self, parent_, summary_, in_model_):

        super(OutputModel, self).__init__()

        self.__hdr = [
            self.tr("Files"),
            self.tr("Count"),
            self.tr("Size"),
            self.tr("Percentage")]

        self.setHorizontalHeaderLabels(self.__hdr)
        #self.rowsInserted.connect(self.disableOversizeItems)
        self.targetSizeChanged.connect(self.updateTarget)

        self.__par = parent_
        self.__sum = summary_
        self.__imd = in_model_

    def sortSize(self, fa_, rev_):
        fa_.sort(key=lambda ma: self.__imd.
                 item(self.__imd.indexFromItem(self.__imd.
                                               findItems(ma)[0]).row(),
                      1).num(), reverse=rev_)

    def sortTitle(self, fa_, rev_):
        fa_.sort(key=lambda ma: self.__imd.
                 item(self.__imd.indexFromItem(self.__imd.
                                               findItems(ma)[0]).row(),
                      0).name(), reverse=rev_)

    def setLastResult(self, result_, progress_):
        self.__result = result_
        self.applyResult(progress_)

    def fileSize(self, ma_):
        return self.__imd.item(self.__imd.indexFromItem(self.__imd.
                                                        findItems(ma_)[0]).
                               row(), 1).num()

    def applyResult(self, progress_=None):

        if self.__result is not None:

            settings_ = QSettings()

            #try:
            #    self.targetSizeChanged.disconnect()
            #except TypeError:
            #    pass

            self.removeRows(0, self.rowCount())

            for pv_, r_ in enumerate(self.__result):

                fa_ = r_[0]
                ts_ = 0

                for ma_ in fa_:
                    ts_ += self.fileSize(ma_)

                loi_ = LeftOverItem(ts_, self.targetSize(), ts_, True,
                                    Qt.AlignRight)

                #self.targetSizeChanged.connect(loi_.updateToolTip)

                l_ = (MultiFileDragItem(fa_),
                      EchoTooltipItem(r_[1], True, Qt.AlignHCenter),
                      OutputSizeItem(ts_, r_[2]),
                      loi_)

                if int(settings_.value("resultSort", 0)) == 0:
                    self.sortTitle(fa_, False)
                elif int(settings_.value("resultSort", 0)) == 1:
                    self.sortTitle(fa_, True)
                elif int(settings_.value("resultSort", 0)) == 2:
                    self.sortSize(fa_, False)
                else:
                    self.sortSize(fa_, True)

                for i_, ma_ in enumerate(fa_):

                    item_ = self.__imd.item(self.__imd.
                                            indexFromItem(self.__imd.
                                                          findItems(ma_)[0]).
                                            row(), 1)

                    rsit_ = EchoTooltipItem(item_.relativeSizePctString(ts_),
                                            False, Qt.AlignRight)
                    rsit_.setToolTip(self.tr("{0} of {1}").
                                     format(rsit_.text(), r_[2]))

                    l_[0].setChild(i_, 0, IconFileItem(ma_))
                    l_[0].setChild(i_, 1, EchoTooltipItem("1", False,
                                                          Qt.AlignHCenter))
                    l_[0].setChild(i_, 2, EchoTooltipItem(item_.text(), False,
                                                          Qt.AlignRight))
                    l_[0].setChild(i_, 3, rsit_)

                self.appendRow(l_)

                if progress_ is not None and pv_ % 500 == 0:
                    progress_.setValue(pv_)

            self.__par.scrollToBottom()
            self.__sum.setText(self.tr("{} results found").
                               format(str(self.rowCount())))

            self.modelSaveable.emit(self.rowCount() > 0)
            self.resultReady.emit()

    @pyqtSlot(float)
    def updateTarget(self, tts_):
        self.blockSignals(True)
        for r_ in range(0, self.rowCount()):
            item_ = self.item(r_, 3)
            item_.updateToolTip(tts_)
            self.disableOversizeItem(item_)
        self.blockSignals(False)

    @pyqtSlot()
    def saveModel(self):

        f_ = None

        settings = QSettings()
        dir_ = settings.value("saveDir", "qdiskfit.txt")

        try:
            f_ = open(QFileDialog.
                      getSaveFileName(None,
                                      self.tr("Save result"), dir_,
                                      self.tr("Text file (*.txt);;"
                                              "All files (*)"))[0], "wt")

            settings.setValue("saveDir", QFileInfo(f_.name).
                              absoluteFilePath())

            for r_ in range(0, self.rowCount()):
                f_.write("[ ")
                for fi_ in self.item(r_, 0).files():
                    f_.write("\'" + fi_ + "\' ")
                f_.write("]:" + self.item(r_, 1).text() + " = " +
                         self.item(r_, 2).text() + " (" +
                         self.item(r_, 3).text() + ")\n")

        except OSError as e:
            if len(e.filename):
                QMessageBox.critical(None, self.tr("Error saving result"),
                                     "\'" + e.filename + "\': " +
                                     e.strerror + " (" + str(e.errno) + ")")
        finally:
            try:
                if f_ is not None:
                    f_.close()
            except OSError:
                pass

    def columns(self):
        return(2, 0, 1, 2, 3)

    def mimeTypes(self):
        return list("text/uri-list")

    def mimeData(self, indexes):

        urls_ = list()
        mime_ = QMimeData()

        for idx in indexes:
            if idx.column() == 0:
                c_ = 0
                while True:
                    ci_ = self.item(idx.row(), 0).child(c_)
                    c_ += 1
                    if ci_ is not None:
                        urls_.append(QUrl("file://" + ci_.path() +
                                          "/" + ci_.name()))
                    else:
                        break

        mime_.setUrls(urls_)

        return mime_

# kate: indent-mode: python
