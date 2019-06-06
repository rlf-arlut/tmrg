#!/usr/bin/python2

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
                            'plag = tmrg.plag:main',
                            'wrg = tmrg.wrg:main']
    }
)
