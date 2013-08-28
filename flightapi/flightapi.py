#!/usr/bin/env python

from flask import Flask
from flask import abort

import weather

from authentication import Authentication

import json
import os
import logging


# "loggin" crap

format = '%(asctime)s [%(name)s] [%(levelname)s] %(message)s'
DEBUG = bool(os.environ.get('FAPIDEBUG', False))
level = logging.DEBUG if DEBUG else logging.INFO
logging.basicConfig(format=format, level=level)

fapi = Flask(__name__)

auth = Authentication(fapi)

@fapi.route('/api/taf/<station>', methods=['GET'])
@auth.required
def taf(station):
    taf = {}
    try:
        taf['station'] = weather.get_taf(station)
        print taf
        return json.dumps({'METAR': taf})
    except Exception as e:
        print e.print_tb()
        return json.dumps("Error: %s" % station)


@fapi.route('/api/metar/<station>', methods=['GET'])
@auth.required
def metar(station):
    metar = {}
    try:
        metar[station] = str(weather.get_parsed_metar(station).code)
        return json.dumps(metar)
    except Exception as e:
        print e
        return json.dumps("Error: %s" % station)
        abort(500)


@fapi.route('/api/long_metar/<station>', methods=['GET'])
@auth.required
def long_metar(station):
    metar = {}
    try:
        # I think this could be better.
        metar = weather.get_parsed_metar(station)

        report = weather.metar_as_dict(metar)
        logging.debug(report)
        return json.dumps(report)
    except Exception as e:
        print e
        return json.dumps("Error: %s" % station)
        abort(500)

# Default routes
@fapi.route('/')
def nope():
    abort(404)


@fapi.route('/favicon.ico')
def go_home_you_are_drunk():
    abort(410)




if __name__ == '__main__':
    fapi.run()
