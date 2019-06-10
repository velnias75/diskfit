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
from PyQt5.QtCore import QFileInfo
from ...util.hrsize import HRSize
from .echotooltipitem import EchoTooltipItem


class HRFileItem(EchoTooltipItem):

    __size = None
    __size_str = None

    def __init__(self, file_):

        super(HRFileItem, self).__init__(file_)

        self.setTextAlignment(Qt.AlignRight)

        self.__size = QFileInfo(file_).size()
        self.__size_str = HRSize.sizeString(self.__size)

    def type(self):
        return EchoTooltipItem.UserType

    def relativeSizePctString(self, total_size_):
        return format(float(self.__size * 100)/float(total_size_), ".3f") + "%"

    def data(self, role):
        if role == Qt.DisplayRole or role == Qt.ToolTipRole:
            return str(self.__size_str)

        return super(HRFileItem, self).data(role)

    def num(self):
        return self.__size

# kate: indent-mode: python
