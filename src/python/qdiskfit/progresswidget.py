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

from PyQt5.QtWidgets import QWidget
from .mainwindow.progress import Ui_progressWidget


class ProgressWidget(QWidget):

    __ui = None

    def __init__(self, actStop_, parent=None):
        super(ProgressWidget, self).__init__(parent)

        self.__ui = Ui_progressWidget()
        self.__ui.setupUi(self)

        self.__ui.stopButton.setIcon(actStop_.icon())
        self.__ui.stopButton.setToolTip(actStop_.toolTip())
        self.__ui.stopButton.clicked.connect(actStop_.trigger)

    def setMinimum(self, min):
        self.__ui.progressBar.setMinimum(min)

    def setMaximum(self, max):
        self.__ui.progressBar.setMaximum(max)

    def setValue(self, val):
        self.__ui.progressBar.setValue(val)


# kate: indent-mode: python
