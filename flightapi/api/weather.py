#!/usr/bin/env python

from flask.ext.restful import abort, Resource

from flightapi import weather


class Taf(Resource):
    def get(self, station):
        try:
            return {station: weather.get_taf(station)}
        except Exception:
            abort(404, message='Cannot find TAF for %s' % (station, ))


class Metar(Resource):
    def get(self, station):
        try:
            return {station: weather.get_parsed_metar(station).code}
        except Exception:
            abort(404, message='Cannot find METAR for %s' % (station, ))


class LongMetar(Resource):
    def get(self, station):
        try:
            metar = weather.get_parsed_metar(station)
            return weather.metar_as_dict(metar)
        except Exception:
            abort(404, message='Cannot find METAR for %s' % (station, ))
