#!/usr/bin/env python
#
# -*- mode:python; sh-basic-offset:4; indent-tabs-mode:nil; coding:utf-8 -*-
# vim:set tabstop=4 softtabstop=4 expandtab shiftwidth=4 fileencoding=utf-8:
#

import os
import setuptools
import sys

import flightapi


readme = open(os.path.join(os.path.dirname(sys.argv[0]),
              'README.rst'), 'rb').read()
reqs = open(os.path.join(os.path.dirname(sys.argv[0]),
              'requirements.txt'), 'rb')

setuptools.setup(
    author='James Scott',
    author_email='scottjab@gmail.com',
    name=flightapi.NAME,
    version=flightapi.VERSION,
    description=flightapi.DESC,
    long_description=readme,
    license='BSD',
    install_requires=reqs.readlines(),
    entry_points = {
        'console_scripts': [
            'flightapid = flightapi.flightapi:main',
        ],
    },
    packages=setuptools.find_packages(),
    include_package_data=True,
)
