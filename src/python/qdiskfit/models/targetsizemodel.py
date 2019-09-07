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
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import pyqtSlot


class TargetSizeModel(QStandardItemModel):

    targetSizeChanged = pyqtSignal(float)

    __tsz = 0.0

    def __init__(self):
        super(TargetSizeModel, self).__init__()

    @pyqtSlot(float)
    def setTargetSize(self, target_):
        self.__tsz = target_
        self.targetSizeChanged.emit(self.__tsz)
        self.disableOversizeItems()

    def targetSize(self):
        return self.__tsz

    def columns(self):
        raise NotImplementedError("columns() not implemented yet")

    @pyqtSlot()
    def disableOversizeItems(self):
        if self.targetSize() is not None:
            for r in range(0, self.rowCount()):
                oversized_ = (self.item(r, self.columns()[0]).num() >
                              self.targetSize())
                for i_, v_ in enumerate(self.columns(), start=1):
                    self.item(r, v_).setEnabled(not oversized_)

# kate: indent-mode: python
