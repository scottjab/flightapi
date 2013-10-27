#!/usr/bin/env python

from flask import Flask, request, g
from flask.ext.restful import Resource, abort

from flightapi.navigation import Navigation

app = Flask(__name__)


class Navaid(Resource):
    def get(self, ident):
        if ident is not None:
            ident = ident.upper()
            nav = Navigation(g.eng)
            navaid = nav.get_waypoint(ident)
            if navaid is not None and len(navaid) > 0:
                return {'navaids': navaid}
            else:
                abort(404, message='Navaid %s not found ' % ident)
        abort(404, message='Missing navaid ident')


class Airway(Resource):
    def put(self):
        if request.json is not None:
            nav = Navigation(g.eng)
            try:
                entry = request.json['entry']
                airway = request.json['airway']
                exit = request.json['exit']
                airway = nav.get_airway(entry, airway, exit)
                return {'airway': airway}
            except KeyError as e:
                abort(404, message='Airway JSON missing: %s' % e)
        abort(404, message='Missing Airway')


class Route(Resource):
    def put(self):
        if request.json is not None:
            nav = Navigation(g.eng)
            try:
                route = request.json['route']
                expanded_route = nav.parser(route)
                # I need some better error handling here.
                return {'route': expanded_route}
            except KeyError:
                abort(404, 'Missing route key')
        abort(404, 'Valid put data is required')
