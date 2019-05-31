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


class TargetNameItem(ValidatingItem):

    __model = None
    __in_rc = True

    def __init__(self, name_, model_, in_rc_=True):
        super(TargetNameItem, self).__init__(name_)
        self.__model = model_
        self.__in_rc = in_rc_

    def validate(self, value):

        if not self.__in_rc:
            for r_ in range(0, self.__model.rowCount()):
                if self.__model.item(r_, 0) is not self and \
                   self.__model.item(r_, 0).text() == value:
                    return False

        return len(value) > 0 and " " not in value

    def convertValue(self, value):
        return str(value)

# kate: indent-mode: python
