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

from PyQt5.QtCore import QFileInfo
from PyQt5.QtWidgets import QFileIconProvider
from .echotooltipitem import EchoTooltipItem


class IconFileItem(EchoTooltipItem):

    def __init__(self, file_):

        fi_ = QFileInfo(file_)
        if fi_.isSymLink():
            fp_ = fi_.symLinkTarget()
        else:
            fp_ = file_

        super(IconFileItem, self).__init__(fp_)

        self.setIcon(QFileIconProvider().icon(fi_))
