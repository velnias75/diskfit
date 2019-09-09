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
    __csz = 0.0
    __ts = 0.0

    __exceedng_txt = None
    __leftover_txt = None

    def __init__(self, ts_, tts_, cumsize_, drag_=False, align_=Qt.AlignLeft):
        super(LeftOverItem, self).__init__("", drag_, align_)

        self.__exceedng_txt = QCoreApplication. \
            translate("LeftOverItem", "exceeds target")

        self.__leftover_txt = QCoreApplication.translate("LeftOverItem",
                                                         "{0} left")

        self.__ts = ts_
        self.__csz = cumsize_
        self.updateToolTip(tts_)

    def updateToolTip(self, tts_):

        leftover_ = tts_ - self.__csz

        self.setText("%.3f %%" % ((float(self.__ts) * 100.0) / tts_))
        self.setToolTip("".join((self.text(), " / ",
                                 (self.__leftover_txt.
                                  format(HRSize.sizeString(leftover_, 0)))
                                 if leftover_ >= 0.0
                                 else self.__exceedng_txt)))

# kate: indent-mode: python
