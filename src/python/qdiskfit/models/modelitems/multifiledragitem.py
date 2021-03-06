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

from .echotooltipitem import EchoTooltipItem
from PyQt5.QtGui import QIcon


class MultiFileDragItem(EchoTooltipItem):

    __files = None

    def __init__(self, files_):
        super(MultiFileDragItem, self).__init__(", ".join(sorted(files_)),
                                                True)
        self.__files = sorted(files_)
        self.setIcon(QIcon.fromTheme("folder"))

    def files(self):
        return self.__files

# kate: indent-mode: python
