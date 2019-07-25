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

from PyQt5.QtGui import QStandardItem
from PyQt5.QtGui import QBrush
from PyQt5.QtCore import Qt


class ValidatingItem(QStandardItem):

    def __init__(self, data_):
        super(ValidatingItem, self).__init__()
        self.setData(self.convertValue(data_), Qt.UserRole+1)
        self.setTextAlignment(Qt.AlignVCenter)

    def isValid(self):
        return self.validate(self.convertValue(super(ValidatingItem, self).
                                               data(Qt.UserRole+1)))

    def validate(self, value):
        raise NotImplementedError

    def displayValue(self, value):
        return str(value)

    def convertValue(self, value):
        raise NotImplementedError

    def data(self, role=Qt.UserRole+1):
        if role == Qt.DisplayRole:
            return self.displayValue(super(ValidatingItem, self).
                                     data(Qt.UserRole+1))
        elif role == Qt.EditRole:
            return str(super(ValidatingItem, self).data(Qt.UserRole+1))
        elif role == Qt.BackgroundRole:
            if self.isValid():
                return super(ValidatingItem, self).data(Qt.BackgroundRole)
            else:
                return QBrush(Qt.red)

        return super(ValidatingItem, self).data(role)

    def setData(self, value, role=Qt.UserRole+1):
        if role == Qt.EditRole:
            super(ValidatingItem, self).setData(self.convertValue(value),
                                                Qt.UserRole+1)

        super(ValidatingItem, self).setData(value, role)

# kate: indent-mode: python
