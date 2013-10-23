#!/usr/bin/env python

from flask import Flask
from flask.ext.restful import Resource, abort

from flightapi.navigation import Navigation

app = Flask(__name__)


class Airport(Resource):
    def get(self, icao):
        if icao is not None:
            icao = icao.upper()
            nav = Navigation(app.eng)
            airport = nav.get_airport(icao)
            if airport is None:
                abort(404, message='Cannot find Airport info for: %s' % icao)
            try:
                airport['ICAO'] = icao
                return airport
            except TypeError:
                abort(500, message='Error encoding airport data')
        abort(404, message='An airport icao is needed')

