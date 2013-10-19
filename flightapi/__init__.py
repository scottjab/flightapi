#!/usr/bin/env python
#
# -*- mode:python; sh-basic-offset:4; indent-tabs-mode:nil; coding:utf-8 -*-
# vim:set tabstop=4 softtabstop=4 expandtab shiftwidth=4 fileencoding=utf-8:
#

import os

VERSION = '0.0.1'
NAME = 'flightapi'
DESC = 'An api that has basic navigation routing and weather.'

from flightapi import fapi


def main():
    debug = bool(os.environ.get("FAPI_DEBUG", None))
    fapi.debug = debug
    fapi.run()

if __name__ == '__main__':
    main()
