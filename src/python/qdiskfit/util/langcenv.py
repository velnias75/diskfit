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

from PyQt5.QtCore import QProcessEnvironment


class LangCProcessEnvironment:

    def env(self):
        dc_env_ = QProcessEnvironment.systemEnvironment()
        dc_env_.remove("LANG")
        dc_env_.insert("LANG", "C")
        dc_env_.remove("LC_ALL")
        dc_env_.insert("LC_ALL", "C")

        return dc_env_

# kate: indent-mode: python
