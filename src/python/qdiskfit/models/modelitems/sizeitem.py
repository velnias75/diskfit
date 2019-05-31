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

from .validatingitem import ValidatingItem
from ...util.hrsize import HRSize
from PyQt5.QtCore import Qt


class SizeItem(ValidatingItem):

    def __init__(self, dbl_):
        super(SizeItem, self).__init__(dbl_)
        self.setTextAlignment(Qt.AlignRight)

    def validate(self, value):
        return value > 0 and value <= 18446744073709551616

    def displayValue(self, value):
        return HRSize(5).sizeString(self.data(Qt.UserRole+1))

    def convertValue(self, value):
        return int(value)

# kate: indent-mode: python
