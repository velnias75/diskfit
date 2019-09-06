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
from PyQt5.QtCore import QCoreApplication
from .echotooltipitem import EchoTooltipItem
from ...util.hrsize import HRSize


class LeftOverItem(EchoTooltipItem):

    def __init__(self, txt_, leftover_, drag_=False, align_=Qt.AlignLeft):
        super(LeftOverItem, self).__init__(txt_)
        tt_ = super(LeftOverItem, self).toolTip() + " / " + \
            QCoreApplication.translate("LeftOverItem", "{0} left"). \
            format(HRSize.sizeString(leftover_, 0))
        self.setToolTip(tt_)

# kate: indent-mode: python
