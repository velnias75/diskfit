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

import os
import setuptools
from setuptools.command.egg_info import egg_info


class EggInfoCommand(egg_info):

    def run(self):
        if "build" in self.distribution.command_obj:
            build_command = self.distribution.command_obj["build"]

            self.egg_base = build_command.build_base

            self.egg_info = os.path.join(self.egg_base,
                                         os.path.basename(self.egg_info))

        egg_info.run(self)


SRC_PATH = os.path.relpath(os.path.join(os.path.dirname(__file__), "."))

setuptools.setup(name='qdiskfit',
                 version='2.0.3.0',
                 description='Simple disk fit calculator (GUI)',
                 url='https://github.com/velnias75/diskfit',
                 author='Heiko Schaefer',
                 author_email='heiko@rangun.de',
                 packages=setuptools.find_packages(),
                 package_dir={
                    "": SRC_PATH,
                    },
                 package_data={
                    '': ['*.ui'],
                    '': ['*.svgz'],
                    '': ['*.pro'],
                    '': ['*.ts'],
                    '': ['*.qm'],
                    '': ['*.desktop']
                    },
                 entry_points={
                     'gui_scripts': [
                         'qdiskfit = qdiskfit.qdiskfit:main'
                         ]
                     },
                 classifiers=[
                     "Programming Language :: Python :: 3",
                     "License :: OSI Approved :: GNU General Public License "
                     "v3 (GPLv3)",
                     "Operating System :: POSIX :: Linux"])
