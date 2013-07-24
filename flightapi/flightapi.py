#!/usr/bin/env python

from flask import Flask
from flask import abort

from bs4 import BeautifulSoup

import pymetar
import requests
from pymetar import NetworkException
import json
import os
import logging


# "loggin" crap

format = '%(asctime)s [%(name)s] [%(levelname)s] %(message)s'
DEBUG = bool(os.environ.get('FAPIDEBUG', False))
level = logging.DEBUG if DEBUG else logging.INFO
logging.basicConfig(format=format, level=level)

fapi = Flask(__name__)


@fapi.route('/api/taf/<station>', methods=['GET'])
def taf(station):
    taf = {}
    try:
        taf['station'] = get_taf(station)
        print taf
        return json.dumps({'METAR': taf})
    except Exception as e:
        print e.print_tb()
        return json.dumps("Error: %s" % station)


@fapi.route('/api/metar/<station>', methods=['GET'])
def metar(station):
    metar = {}
    try:
        metar[station] = str(get_parsed_metar(station).code)
        return json.dumps(metar)
    except Exception as e:
        print e
        return json.dumps("Error: %s" % station)
        abort(500)


@fapi.route('/api/long_metar/<station>', methods=['GET'])
def long_metar(station):
    metar = {}
    try:
        # I think this could be better.
        metar = get_parsed_metar(station)

        report = metar_as_dict(metar)
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


# private methods

def get_taf(station):
    taf_service = "http://weather.noaa.gov/cgi-bin/mgettaf.pl?cccc=%s"
    try:
        parsed_html = BeautifulSoup(requests.get(taf_service % station).content)
        parsed_taf = parsed_html.find('pre').text
        parsed_taf = parsed_taf.replace('\n', '')
        return parsed_taf
    except Exception as e:
        raise e


def get_parsed_metar(station):
    report = ""
    try:
        fetcher = pymetar.ReportFetcher(station)
        rep = fetcher.FetchReport()
        report = pymetar.ReportParser().ParseReport(rep)
        return report
    except NetworkException as e:
        raise e
    return str(report)


def metar_as_dict(metar):
    report = {}
    report['cloud_info'] = metar.getCloudinfo()
    report['cloud_type'] = metar.getCloudtype()
    report['conditions'] = metar.getConditions()
    report['cycle'] = metar.getCycle()
    report['dew_point_c'] = metar.getDewPointCelsius()
    report['dew_point_f'] = metar.getDewPointFahrenheit()
    report['full_report'] = metar.getFullReport()
    report['humidity'] = metar.getHumidity()
    report['iso_time'] = metar.getISOTime()
    report['pixmap'] = metar.getPixmap()
    report['pressure'] = metar.getPressure()
    report['pressure_hg'] = metar.getPressuremmHg()
    report['raw_metar'] = metar.getRawMetarCode()
    report['report_url'] = metar.getReportURL()
    report['sky_conditions'] = metar.getSkyConditions()
    report['station_alt'] = metar.getStationAltitude()
    report['station_city'] = metar.getStationCity()
    report['station_country'] = metar.getStationCountry()
    report['station_lat'] = metar.getStationLatitude()
    report['station_lat_f'] = metar.getStationLatitudeFloat()
    report['station_lon'] = metar.getStationLongitude()
    report['station_lon_f'] = metar.getStationLongitudeFloat()
    report['station_name'] = metar.getStationName()
    report['station_pos'] = metar.getStationPosition()
    report['station_pos_f'] = metar.getStationPositionFloat()
    report['temp'] = metar.getTemperatureCelsius()
    report['temp_f'] = metar.getTemperatureFahrenheit()
    report['time'] = metar.getTime()
    report['vis_k'] = metar.getVisibilityKilometers()
    report['vis'] = metar.getVisibilityMiles()
    report['weather'] = metar.getWeather()
    report['wind_compus'] = metar.getWindCompass()
    report['wind_direction'] = metar.getWindDirection()
    report['wind_speed'] = metar.getWindSpeed()
    report['wind_speed_beaufort'] = metar.getWindSpeedBeaufort()
    report['wind_speed_knots'] = metar.getWindSpeedKnots()
    report['wind_speed_mph'] = metar.getWindSpeedMilesPerHour()
    report['windchill'] = metar.getWindchill()
    report['windchill'] = metar.getWindchillF()
    return report

if __name__ == '__main__':
    fapi.run()
