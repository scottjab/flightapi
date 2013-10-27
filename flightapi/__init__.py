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
    host = os.environ.get('FAPIHOST', '127.0.0.1')
    debug = bool(os.environ.get('FAPIDEBUG', None))
    fapi.debug = debug
    fapi.run(host=host)

if __name__ == '__main__':
    main()
