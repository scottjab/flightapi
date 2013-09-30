#!/usr/bin/env python

from flask import Flask
from flask import abort, request

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


@fapi.route('/api/distance', methods=['PUT'])
@auth.required
def distance():
    if request.method == 'PUT':
        if request.data is not None:
            try:
                data = json.loads(request.data)
                source = data['source']
                destination = data['destination']
                nautical_miles = Navigation.distance(source, destination)
                distance = {}
                distance['NM'] = nautical_miles
                distance['km'] = nautical_miles * 1.852
                distance['mi'] = nautical_miles * 1.150779
                return json.dumps(distance)
            except ValueError:
                json.dumps("Error: JSON PARSING FAILED")
                abort(500)


# I may want to change this to a PUT.
@fapi.route('/api/airport/<airport>', metheds=['GET'])
@auth.required
def apt(airport):
    if airport is not None:
        airport = Navigation.get_airport_info(airport)
        if airport is None:
            return json.dumps('Airport not found')
        # I may overload this, but this will work for now
        try:
            return json.dumps(airport)
        except TypeError:
            return json.dumps('ERROR: encoding airport data')
            abort(500)
    else:
        return json.dumps('ERRER: need an airport ICAO')


@fapi.route('/api/navaid/<id>', methods=['GET'])
@auth.required
def navaid(navaid_id):
    if navaid_id is not None:
        navaid = Navigation.get_navaid_info(navaid_id)
        if navaid is None:
            return json.dumps('Navaid not found')
        try:
            return json.dumps(navaid)
        except TypeError:
            return json.dumps('ERROR: encoding navaid data')


# Default routes
@fapi.route('/')
def nope():
    abort(404)


@fapi.route('/favicon.ico')
def go_home_you_are_drunk():
    abort(410)

if __name__ == '__main__':
    fapi.run()
