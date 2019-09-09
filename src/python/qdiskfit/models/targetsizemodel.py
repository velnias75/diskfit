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

from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtCore import QModelIndex
from PyQt5.QtCore import pyqtSlot


class TargetSizeModel(QStandardItemModel):

    __tsz = 0.0
    __osc = True

    def __init__(self, oversizeCheck=True):
        super(TargetSizeModel, self).__init__()
        self.__osc = oversizeCheck

    @pyqtSlot(float)
    def setTargetSize(self, target_):
            self.__tsz = target_
            self.updateTarget(self.__tsz)

    def targetSize(self):
        return self.__tsz

    def enabledItems(self):

        ei_ = 0 if self.__osc else self.rowCount()

        for r_ in range(0, self.rowCount()):
            if self.item(r_, 0).isEnabled():
                ei_ += 1

        return ei_

    def columns(self):
        raise NotImplementedError("columns() not implemented yet")

    @pyqtSlot("QStandardItem*")
    def disableOversizeItem(self, item_):

        idx_ = self.indexFromItem(item_)

        if idx_.isValid():
            row_ = idx_.row()
            self.disableOversizeItems(idx_, row_, row_)

    @pyqtSlot(QModelIndex, int, int)
    def disableOversizeItems(self, idx_=QModelIndex(), first_=-1, last_=-1):

        if self.__osc and self.__tsz is not None:

            cls_ = self.columns()
            rit_ = []

            for r in range(first_ if first_ != -1 else 0,
                           last_ + 1 if last_ != -1 else self.rowCount()):

                for i_ in cls_:
                    rit_.append(self.item(r, i_))

                ena_ = rit_[0].num() <= self.__tsz

                for i_ in range(1, len(rit_)):
                    rit_[i_].setEnabled(ena_)
                    if rit_[i_].hasChildren():
                        for cr_ in range(rit_[i_].rowCount()):
                            for cc_ in range(rit_[i_].columnCount()):
                                rit_[i_].child(cr_, cc_).setEnabled(ena_)

                rit_ *= 0

    def updateTarget(self, tts_):
        pass

# kate: indent-mode: python
