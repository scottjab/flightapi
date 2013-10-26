#!/usr/bin/env python

from flask import Flask, abort, g
from flask.ext.restful import Api

from sqlalchemy import create_engine

from authentication import Authentication

from api.weather import LongMetar, Metar, Taf
from api.airport import Airport
from api.navaids import Airway, Navaid, Route

import json
import os
import logging


# "loggin" crap

format = '%(asctime)s [%(name)s] [%(levelname)s] %(message)s'
DEBUG = bool(os.environ.get('FAPIDEBUG', False))
level = logging.DEBUG if DEBUG else logging.INFO
logging.basicConfig(format=format, level=level)
conf = os.environ.get('FAPICONF', 'flightapi.json')
conf = os.path.realpath(conf)
CONF = {}
try:
    logging.info('Loading %s configuration file' % (conf, ))
    CONF = json.load(open(conf, 'rb'))
except Exception as e:
    logging.warning('Could not load configuration file: %r' % (e,))


fapi = Flask(__name__)

auth = Authentication(fapi)
api = Api(fapi)
eng = create_engine('mysql+mysqldb://%s:%s@%s/%s' % (CONF['dbuser'],
                                                            CONF['dbpass'],
                                                            CONF['dbhost'],
                                                            CONF['db']),
                    pool_size=2,
                    pool_recycle=3600,
                    echo=False)
ctx = fapi.app_context()
ctx.push()
g.eng = eng

# Default routes
@fapi.route('/')
def nope():
    abort(404)


@fapi.route('/favicon.ico')
def go_home_you_are_drunk():
    abort(410)

# Api fun
# weather methods
api.add_resource(Metar, '/api/metar/<station>')
api.add_resource(LongMetar, '/api/longmetar/<station>')
api.add_resource(Taf, '/api/taf/<station>')

# Airport methods
api.add_resource(Airport, '/api/airport/<icao>')

# Navaid methods
api.add_resource(Airway, '/api/airway')
api.add_resource(Navaid, '/api/navaid/<ident>')
api.add_resource(Route, '/api/route')


if __name__ == '__main__':
    fapi.run()
