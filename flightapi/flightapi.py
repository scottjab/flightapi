#!/usr/bin/env python

from flask import Flask, jsonify
from flask import abort, request

from sqlalchemy import create_engine

import weather

from authentication import Authentication

from navigation import Navigation

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

eng = create_engine('mysql+mysqldb://%s:%s@%s/%s' % (CONF['dbuser'],
                                                     CONF['dbpass'],
                                                     CONF['dbhost'],
                                                     CONF['db']),
                    pool_size=2,
                    pool_recycle=3600,
                    echo=False)


@fapi.route('/api/taf/<station>', methods=['GET'])
@auth.required
def taf(station):
    taf = {}
    try:
        taf['station'] = weather.get_taf(station)
        print taf
        return jsonify({'METAR': taf})
    except Exception as e:
        print e.print_tb()
        return jsonify("Error: %s" % station)


@fapi.route('/api/metar/<station>', methods=['GET'])
@auth.required
def metar(station):
    metar = {}
    try:
        metar[station] = str(weather.get_parsed_metar(station).code)
        return jsonify(metar)
    except Exception as e:
        print e
        return jsonify("Error: %s" % station)
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
        return jsonify(report)
    except Exception as e:
        print e
        return jsonify("Error: %s" % station)
        abort(500)


@fapi.route('/api/distance', methods=['PUT'])
@auth.required
def distance():
    nav = Navigation(eng)
    if request.method == 'PUT':
        if request.data is not None:
            try:
                data = json.loads(request.data)
                source = data['source'].upper()
                destination = data['destination'].upper()
                nautical_miles = nav.distance_by_name(source, destination)
                distance = {}
                distance['NM'] = nautical_miles
                distance['km'] = nautical_miles * 1.852
                distance['mi'] = nautical_miles * 1.150779
                return jsonify(distance)
            except ValueError:
                jsonify("Error: JSON PARSING FAILED")
                abort(500)


# I may want to change this to a PUT.
@fapi.route('/api/airport/<icao>', methods=['GET'])
@auth.required
def apt(icao):
    icao = icao.upper()
    nav = Navigation(eng)
    if icao is not None:
        airport = nav.get_airport_info(icao)
        if airport is None:
            return jsonify('Airport not found')
        # I may overload this, but this will work for now
        try:
            airport['ICAO'] = icao
            return jsonify(airport)
        except TypeError:
            return jsonify('ERROR: encoding airport data')
            abort(500)
    else:
        return jsonify('ERRER: need an airport ICAO')


@fapi.route('/api/navaid/<navaid_id>', methods=['GET'])
@auth.required
def navaid(navaid_id):
    nav = Navigation(eng)
    if navaid_id is not None:
        navaid = nav.get_waypoint(navaid_id)
        if navaid is None:
            return jsonify('Navaid not found')
        try:
            import pprint
            logging.info(pprint.pformat(navaid))
            if len(navaid) > 0:
                return jsonify(navaids=navaid)
            else:
                jsonify('ERROR: %s not found' % (navaid_id, ))
        except TypeError:
            return jsonify('ERROR: encoding navaid data')


# Default routes
@fapi.route('/')
def nope():
    abort(404)


@fapi.route('/favicon.ico')
def go_home_you_are_drunk():
    abort(410)

if __name__ == '__main__':
    fapi.run()
