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

from PyQt5.QtWidgets import QDialog
from .dialogs.exclusive import Ui_ExclusiveDlg
from .models.exclusivemodel import ExclusiveModel


class ExclusiveDlg(QDialog):

    __ui = None
    __em = None

    def __init__(self, parent_=None):

        super(ExclusiveDlg, self).__init__(parent_)

        self.__ui = Ui_ExclusiveDlg()
        self.__ui.setupUi(self)
        self.__em = ExclusiveModel(self.__ui.table_input)
        self.__ui.table_input.setModel(self.__em)

    def diffFiles(self, input_):

        d_ = dict()

        for idx_ in input_.selectionModel().selectedIndexes():
            if idx_.row() not in d_:
                d_[idx_.row()] = list()
                d_[idx_.row()].append(input_.model().
                                      item(idx_.row(), idx_.column()).copy())
            else:
                d_[idx_.row()].append(input_.model().
                                      item(idx_.row(), idx_.column()).copy())
                self.__em.appendRow(d_[idx_.row()])

# kate: indent-mode: python
