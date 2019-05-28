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

import os.path
import json


class Site:

    __instance = None

    class __Site:

        siteJSON_ = None

        def __init__(self):

            siteJSONFile_ = os.path.dirname(os.path.realpath(__file__)) + \
                "/site.json"

            if os.path.isfile(siteJSONFile_):
                with open(siteJSONFile_) as json_conf:
                    self.siteJSON_ = json.load(json_conf)

        def get(self, name_, default_):
            if self.siteJSON_ is not None:
                return self.siteJSON_.get(name_, default_)
            return default_

    def __init__(self):
        if not Site.__instance:
            Site.__instance = Site.__Site()

    def __getattr__(self, atname_):
        return getattr(self.__instance, atname_)

# kate: indent-mode: python
