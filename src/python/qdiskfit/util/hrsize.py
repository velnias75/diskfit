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

from math import log
from math import trunc


class HRSize:

    __dec = 2

    def __init__(self, dec_=2):
        self.__dec = dec_

    def __getFormatted(self, size_):

        if trunc(size_) == size_:
            format_ = ".0f"
        else:
            format_ = "." + str(self.__dec) + "f"

        return format(size_, format_)

    def sizeString(self, size_):

        if size_ > 0:
            d_ = log(size_, 2)
        else:
            d_ = 0

        if d_ >= 30.0:
            return self.__getFormatted(size_/1073741824.0) + " GByte"
        elif d_ >= 20.0:
            return self.__getFormatted(size_/1048576.0) + " MByte"
        elif d_ >= 10.0:
            return self.__getFormatted(size_/1024.0) + " KByte"

        return str(size_) + " Byte"

# kate: indent-mode: python