#!/usr/bin/python2

# Copyright (c) CERN and the TMRG authors.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import setuptools

setuptools.setup(
    name='tmrg',
    version="0.1alpha",
    description='TMRG Triple Modular Redundancy Generator',
    author='EP-ESE-ME, CERN',
    packages=['tmrg'],
    entry_points={
        'console_scripts': ['tmrg = tmrg.tmrg:main',
                            'seeg = tmrg.seeg:main',
                            'tbg = tmrg.tbg:main',
                            'plag = tmrg.plag:main',
                            'wrg = tmrg.wrg:main']
    }
)
