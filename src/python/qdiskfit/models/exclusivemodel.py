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

from PyQt5.QtCore import QUrl
from PyQt5.QtCore import QMimeData
from .inputmodel import InputModel


class ExclusiveModel(InputModel):

    def __init__(self, parent_):
        super(ExclusiveModel, self).__init__(parent_, None, None, None, None,
                                             False)

    def mimeTypes(self):
        return list("text/uri-list")

    def mimeData(self, indexes):

        urls_ = list()
        mime_ = QMimeData()

        for idx in indexes:
            if idx.column() == 0:
                urls_.append(QUrl("file://" + self.item(idx.row(), 0).text()))

        mime_.setUrls(urls_)

        return mime_


# kate: indent-mode: python
