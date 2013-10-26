#!/usr/bin/env python

from flask import g
from flask.ext.restful import Resource, abort

from flightapi.navigation import Navigation


class Airport(Resource):

    def get(self, icao):
        if icao is not None:
            icao = icao.upper()
            nav = Navigation(g.eng)
            airport = nav.get_airport(icao)
            if airport is None:
                abort(404, message='Cannot find Airport info for: %s' % icao)
            try:
                airport['ICAO'] = icao
                return airport
            except TypeError:
                abort(500, message='Error encoding airport data')
        abort(404, message='An airport icao is needed')

