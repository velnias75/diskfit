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

from PyQt5.QtWidgets import QApplication
from shutil import which
from shlex import quote
import subprocess
import notify2
import os
import re


class Notify:

    __instance = None

    class __Notify:

        __appn = None
        __nini = None
        __noti = None
        __kcli = None

        def __init__(self):
            self.__appn = "%s v%s" % (QApplication.applicationName(),
                                      QApplication.applicationVersion())
            self.__nini = notify2.init(self.__appn)
            self.__noti = notify2.Notification("", "", "qdiskfit")
            self.__kcli = which('kdeconnect-cli')

        def __del__(self):
            notify2.uninit()

        def message(self, msg_):

            self.__noti.update("", msg_, "qdiskfit")
            self.__noti.set_timeout(8000)
            self.__noti.set_urgency(notify2.URGENCY_NORMAL)
            self.__noti.show()

            if self.__kcli is not None:

                my_env_ = os.environ.copy()
                my_env_["LANG"] = "C"

                devices_ = []

                proc_ = subprocess.Popen([self.__kcli, '-a'],
                                         stdout=subprocess.PIPE,
                                         env=my_env_)
                while True:
                    line_ = proc_.stdout.readline()
                    if not line_:
                        break

                    dev_match_ = re.compile('[^:]+: ([^\s]+).*'). \
                        match(str(line_.rstrip()))

                    if dev_match_ is not None:
                        devices_.append(dev_match_.group(1))

                pmsg_ = "%s: %s" % (self.__appn, msg_)

                for d_ in devices_:
                    os.system(self.__kcli + " -d " + d_ + " --ping-msg " +
                              quote(pmsg_))

    def __new__(cls):
        if not Notify.__instance:
            Notify.__instance = Notify.__Notify()
        return Notify.__instance

    def __getattr__(self, atname_):
        return getattr(self.__instance, atname_)

# kate: indent-mode: python
