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

from PyQt5.QtCore import QProcess
from .langcenv import LangCProcessEnvironment
from ..site import Site
import tempfile


class DiskFitProcess(QProcess):

    def __init__(self):

        super(DiskFitProcess, self).__init__()

        df_env_ = LangCProcessEnvironment().env()
        df_env_.remove("DISKFIT_STRIPDIR")
        df_env_.insert("DISKFIT_XMLOUT", "1")
        df_env_.insert("LANG", "C")

        self.setProcessEnvironment(df_env_)
        self.setWorkingDirectory(tempfile.gettempdir())

    def runDiskFit(self, args_=[]):
        self.start(self.diskfitPath(), args_, DiskFitProcess.ReadOnly |
                   DiskFitProcess.Unbuffered)

    @staticmethod
    def diskfitPath():
        return Site().get("diskfitPath", "/usr/bin/diskfit")

# kate: indent-mode: python
