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
from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import QCoreApplication
from .echotooltipitem import EchoTooltipItem
from ...util.hrsize import HRSize


class LeftOverItem(EchoTooltipItem):

    __upd = None

    class __updater(QObject):

        __loi = None
        __csz = 0.0
        __ts = 0.0

        def __init__(self, loi_, csz_, ts_):
            QObject.__init__(self)
            self.__loi = loi_
            self.__csz = csz_
            self.__ts = ts_

        @pyqtSlot(float)
        def updateToolTip(self, tts_):

            leftover_ = tts_ - self.__csz

            self.__loi.setText(format(((float(self.__ts) * 100.0) / tts_),
                                      ".3f") + "%")
            self.__loi.setToolTip(self.__loi.text() + " / " +
                                  QCoreApplication.translate("LeftOverItem",
                                                             "{0} left").
                                  format(HRSize.sizeString(leftover_ if
                                                           leftover_ > 0.0
                                                           else 0.0, 0)))

    def __init__(self, ts_, tts_, cumsize_, drag_=False, align_=Qt.AlignLeft):
        super(LeftOverItem, self).__init__("", drag_, align_)
        self.__upd = LeftOverItem.__updater(self, cumsize_, ts_)
        self.__upd.updateToolTip(tts_)

    def __getattr__(self, atname_):
        return getattr(self.__upd, atname_)

# kate: indent-mode: python
