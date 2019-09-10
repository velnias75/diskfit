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

import gi
from PyQt5.QtCore import QCoreApplication
gi.require_version('Notify', '0.7')
from gi.repository import Notify
from shutil import which
from shlex import quote
import subprocess
import os
import re


class Notify:

    __nini = Notify.init("KDEConnect")
    __noti = Notify.Notification.new("", None, "qdiskfit")

    def __del__(self):
        Notify.uninit()

    @staticmethod
    def message(msg_):

        app_ = "%s v%s" % (QCoreApplication.applicationName(),
                           QCoreApplication.applicationVersion())

        kcli_ = which('kdeconnect-cli')

        if kcli_ is not None:

            my_env_ = os.environ.copy()
            my_env_["LANG"] = "C"

            devices_ = []

            proc_ = subprocess.Popen([kcli_, '-a'], stdout=subprocess.PIPE,
                                     env=my_env_)
            while True:
                line_ = proc_.stdout.readline()
                if not line_:
                    break

                dev_match_ = re.compile('[^:]+: ([^\s]+).*'). \
                    match(str(line_.rstrip()))

                if dev_match_ is not None:
                    devices_.append(dev_match_.group(1))

            pmsg_ = "%s: %s" % (app_, msg_)

            Notify.__noti.set_app_name(app_)
            Notify.__noti.update(msg_, None, "qdiskfit")
            Notify.__noti.set_timeout(10000)
            Notify.__noti.set_urgency(1)
            Notify.__noti.show()

            for d_ in devices_:
                os.system(kcli_ + " -d " + d_ + " --ping-msg " + quote(pmsg_))

# kate: indent-mode: python
